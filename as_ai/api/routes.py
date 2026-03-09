import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from pydantic import BaseModel

from as_ai.dataset_loader import load_dataset, get_schema
from as_ai.agent import create_agent
from as_ai.logger import log_query

router = APIRouter()

# Directory to save uploaded files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

from as_ai.database.models import get_db, User, Dataset, Team, TeamMember, DatasetInsight, DatasetDashboard
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncio

limiter = Limiter(key_func=get_remote_address)


from as_ai.dataset_loader import load_dataset

def get_user_dataset_df(db, dataset_id_str, user_id):
    try:
        ds_id = int(str(dataset_id_str).replace("dataset_", ""))
    except ValueError:
        return None
    ds = db.query(Dataset).filter(Dataset.id == ds_id).first()
    if not ds: return None
    
    if ds.owner_id != user_id:
        if not ds.team_id:
            return None
        member = db.query(TeamMember).filter(TeamMember.team_id == ds.team_id, TeamMember.user_id == user_id).first()
        if not member:
            return None

    try:
        return load_dataset(ds.file_path)
    except:
        return None

def get_all_user_dfs(db, user_id):
    datasets = db.query(Dataset).filter(Dataset.owner_id == user_id).all()
    
    team_memberships = db.query(TeamMember).filter(TeamMember.user_id == user_id).all()
    team_ids = [m.team_id for m in team_memberships]
    
    if team_ids:
        team_datasets = db.query(Dataset).filter(Dataset.team_id.in_(team_ids)).all()
        existing_ids = {d.id for d in datasets}
        for td in team_datasets:
            if td.id not in existing_ids:
                datasets.append(td)
                
    dfs = []
    ids = []
    for d in datasets:
        try:
            dfs.append(load_dataset(d.file_path))
            ids.append(f"dataset_{d.id}")
        except:
            pass
    return dfs, ids

class TeamCreateRequest(BaseModel):
    name: str

class InviteRequest(BaseModel):
    email: str
    role: str

@router.post("/teams/create")
async def create_team(request: TeamCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    team = Team(name=request.name, owner_id=current_user.id)
    db.add(team)
    db.commit()
    db.refresh(team)
    
    member = TeamMember(team_id=team.id, user_id=current_user.id, role="owner")
    db.add(member)
    db.commit()
    
    return {"message": "Team created successfully", "team_id": team.id}

@router.post("/teams/{team_id}/invite")
async def invite_to_team(team_id: int, request: InviteRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id).first()
    if not member or member.role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Not authorized to invite to this team")
        
    invitee = db.query(User).filter(User.email == request.email).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")
        
    existing_member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == invitee.id).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User already in team")
        
    new_member = TeamMember(team_id=team_id, user_id=invitee.id, role=request.role)
    db.add(new_member)
    db.commit()
    
    return {"message": "User invited successfully"}

@router.get("/teams")
async def get_user_teams(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    teams = []
    for m in memberships:
        # Load team explicitly
        db.refresh(m, ['team'])
        teams.append({
            "id": m.team.id,
            "name": m.team.name,
            "role": m.role
        })
    return {"teams": teams}

@router.get("/teams/{team_id}/datasets")
async def get_team_datasets(team_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == current_user.id).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
        
    datasets = db.query(Dataset).filter(Dataset.team_id == team_id).all()
    return {
        "datasets": [
            {
                "id": d.id,
                "name": d.name,
                "rows": d.rows,
                "columns": d.columns,
                "created_at": d.created_at
            }
            for d in datasets
        ]
    }

class AuthRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/register")
async def register_user(request: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = hash_password(request.password)
    new_user = User(email=request.email, password_hash=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

@router.post("/auth/login")
async def login_user(request: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    access_token = generate_access_token(user.id)
    return {"access_token": access_token}


class AnalystChatRequest(BaseModel):
    dataset_id: str
    question: str

from as_ai.ai_analyst.analyst_engine import analyze_dataset_query
from fastapi import Request, BackgroundTasks

@router.post("/ai_analyst/chat")
@limiter.limit("100/minute")
async def ai_analyst_chat_api(request: Request, body: AnalystChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Executes a dynamic AI analyst agent generating pandas/sklearn logic on the fly.
    """
    df = get_user_dataset_df(db, body.dataset_id, current_user.id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or access denied.")
        
    try:
        response = analyze_dataset_query(df, body.question)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class AskRequest(BaseModel):
    query: str

from as_ai.discovery_engine import DiscoveryEngine
import asyncio
import shutil

from typing import Optional

@router.post("/upload_dataset")
@limiter.limit("100/minute")
async def upload_dataset(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...), team_id: Optional[int] = Form(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Uploads a dataset to the user's specific workspace directory and saves DB metadata.
    Validated for 100MB size and 1,000,000 max rows.
    """
    if not file.filename.endswith((".csv", ".xls", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
    # Validation: Max Upload Size 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB.")

    user_dir = os.path.join(DATA_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    
    file_path = os.path.join(user_dir, file.filename)
    
    # Save the file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        # Load the dataset using the modular loader
        df = load_dataset(file_path)
        
        # Validation: Max Row Count (1,000,000)
        if df.shape[0] > 1000000:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Dataset exceeds 1,000,000 row maximum.")
        
        # Save to DB
        new_dataset = Dataset(
            name=file.filename,
            file_path=file_path,
            owner_id=current_user.id,
            team_id=team_id,
            rows=df.shape[0],
            columns=df.shape[1]
        )
        db.add(new_dataset)
        db.commit()
        db.refresh(new_dataset)
        
        # Background Discovery
        dataset_id = str(new_dataset.id)
        numeric_id = new_dataset.id
        def run_bg_discovery():
            try:
                engine = DiscoveryEngine(dataset_id)
                engine.discover_patterns(df)
            except:
                pass
                
        def run_bg_insights():
            from as_ai.insights.insight_engine import analyze_dataset_insights
            analyze_dataset_insights(numeric_id)
            
        def run_bg_dashboard():
            from as_ai.dashboard.dashboard_engine import generate_dashboard
            generate_dashboard(numeric_id)
        
        # Dispatch background tasks formally via FastAPI
        background_tasks.add_task(run_bg_discovery)
        background_tasks.add_task(run_bg_insights)
        background_tasks.add_task(run_bg_dashboard)
        
        return {
            "message": "dataset uploaded successfully",
            "dataset_id": new_dataset.id,
            "rows": new_dataset.rows,
            "columns": new_dataset.columns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {str(e)}")

@router.get("/datasets")
async def get_datasets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns datasets belonging to the logged-in user.
    """
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()
    return {
        "datasets": [
            {
                "id": d.id,
                "name": d.name,
                "rows": d.rows,
                "columns": d.columns,
                "created_at": d.created_at
            }
            for d in datasets
        ]
    }

@router.get("/datasets/{dataset_id}/data")
async def get_dataset_data(dataset_id: int, limit: int = 1000, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns the raw dataset rows for frontend charting, limited to prevent browser crashes.
    """
    df = get_user_dataset_df(db, f"dataset_{dataset_id}", current_user.id)
    if df is None:
        raise HTTPException(status_code=403, detail="Dataset not found or access denied")
        
    df = df.head(limit)
    # Convert dates to string for JSON serialization
    for col in df.select_dtypes(include=['datetime', 'datetimetz']).columns:
        df[col] = df[col].astype(str)
        
    # Replace NaNs with None for JSON
    df = df.replace({pd.NA: None, np.nan: None})
    
    return {"data": df.to_dict(orient="records")}

@router.get("/datasets/{dataset_id}/dashboard")
async def get_dataset_dashboard(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns AI-generated auto-dashboard config for a dataset.
    """
    df_check = get_user_dataset_df(db, f"dataset_{dataset_id}", current_user.id)
    if df_check is None:
        raise HTTPException(status_code=403, detail="Dataset not found or access denied")
        
    dash = db.query(DatasetDashboard).filter(DatasetDashboard.dataset_id == dataset_id).first()
    if not dash:
        return {"kpis": [], "charts": []}
        
    return dash.dashboard_config

@router.get("/datasets/{dataset_id}/insights")
async def get_dataset_insights(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns AI-generated insights for a given dataset, assuming user has access.
    """
    df_check = get_user_dataset_df(db, f"dataset_{dataset_id}", current_user.id)
    if df_check is None:
        raise HTTPException(status_code=403, detail="Dataset not found or access denied")
        
    insights = db.query(DatasetInsight).filter(DatasetInsight.dataset_id == dataset_id).order_by(DatasetInsight.importance_score.desc()).all()
    
    return {
        "insights": [
            {
                "type": ins.insight_type,
                "description": ins.description,
                "importance": ins.importance_score
            }
            for ins in insights
        ]
    }

@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Deletes a dataset record and removes the physical file.
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
        
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}


@router.post("/ask")
async def ask(request: AskRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Queries the AS-AI Agent loaded with all uploaded datasets.
    """
    dfs, _ = get_all_user_dfs(db, current_user.id)
    if not dfs:
        raise HTTPException(status_code=400, detail="No datasets uploaded. Please upload a dataset first.")
        
    try:
        agent = create_agent(dfs)
        
        # Execute the query
        result = agent.chat(request.query)
        
        chart_path = None
        answer_text = str(result)
        
        # Check if the result is a path to a generated chart
        if isinstance(result, str) and result.endswith('.png') and os.path.isfile(result):
            filename = os.path.basename(result)
            chart_path = f"/charts/{filename}"
            answer_text = "Here is the generated chart."
        
        # Log the request
        log_query(request.query, str(result))
        
        return {
            "query": request.query,
            "answer": answer_text,
            "chart": chart_path
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

from as_ai.insights import generate_dataset_insights

@router.get("/dataset_insights")
async def dataset_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
    insights = {}
    for df, ds_id in zip(dfs, ids):
        insights[ds_id] = generate_dataset_insights(df)
        
    return insights

from as_ai.dashboard import generate_dashboard

@router.get("/generate_dashboard")
async def generate_dashboard_api(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
    response = []
    for df, dataset_id in zip(dfs, ids):
        chart_paths = generate_dashboard(df, dataset_id=dataset_id)
        
        response.append({
            "dataset": dataset_id,
            "dashboard_charts": chart_paths
        })
        
    return response

from typing import Optional
from as_ai.ai_insights import generate_ai_insights, detect_anomalies

@router.get("/ai_analysis")
async def ai_analysis(report: Optional[bool] = False, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
    analysis_results = []
    for df, dataset_id in zip(dfs, ids):
        anomalies = detect_anomalies(df)
        ai_insights = generate_ai_insights(df)
        stats = generate_dataset_insights(df)
        
        if report:
            # Full Report Formatting
            analysis_results.append({
                "dataset": dataset_id,
                "dataset_summary": stats,
                "data_quality": {"missing_values": stats.get("missing_values")},
                "anomalies": anomalies,
                "ai_insights": {
                    "key_trends": ai_insights.get("key_trends"),
                    "business_insights": ai_insights.get("business_insights"),
                    "anomalies_summary": ai_insights.get("anomalies")
                },
                "recommended_charts": ai_insights.get("recommended_visualizations", [])
            })
        else:
            # Standard Formatting
            analysis_results.append({
                "dataset": dataset_id,
                "statistics": stats,
                "anomalies": anomalies,
                "ai_insights": ai_insights
            })
            
    # If only one dataset is present, return it directly or as list? 
    # Usually standard is returning the list but depends on frontend, keeping list to match others.
    if len(analysis_results) == 1:
        return analysis_results[0]
        
    return {"analysis": analysis_results}

from as_ai.autonomous_agent import run_autonomous_analysis

@router.get("/autonomous_analysis")
async def autonomous_analysis_api(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
    autonomous_results = []
    for df, dataset_id in zip(dfs, ids):
        report = run_autonomous_analysis(df, dataset_id=dataset_id)
        
        autonomous_results.append({
            "dataset": dataset_id,
            "analysis": report
        })
        
    if len(autonomous_results) == 1:
        return autonomous_results[0]
        
    return {"autonomous_analysis": autonomous_results}

from pydantic import BaseModel
from as_ai.automl import train_best_model
from as_ai.explainability import generate_shap_explanations
from as_ai.report_generator import generate_pdf_report

class TrainModelRequest(BaseModel):
    dataset_id: str
    target_column: str

@router.post("/train_model")
async def train_model_api(request: TrainModelRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    df = get_user_dataset_df(db, request.dataset_id, current_user.id)
    if df is None: raise HTTPException(status_code=404, detail=f"Dataset '{request.dataset_id}' not found.")

    
    if request.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Target column '{request.target_column}' not in dataset.")
        
    try:
        # Train
        result = train_best_model(df, request.target_column, request.dataset_id)
        
        # Explain
        shap_charts = generate_shap_explanations(
            result["model_obj"], 
            result["X_train"], 
            request.dataset_id, 
            request.target_column
        )
        
        return {
            "best_model": result["best_model"],
            "task_type": result["task_type"],
            "metrics": result["metrics"],
            "feature_importance_chart": result["feature_importance_chart"],
            "shap_summary_chart": shap_charts.get("shap_summary"),
            "shap_dependence_chart": shap_charts.get("shap_dependence")
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class GenerateReportRequest(BaseModel):
    dataset_id: str

@router.post("/generate_report")
async def generate_report_api(request: GenerateReportRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    df = get_user_dataset_df(db, request.dataset_id, current_user.id)
    if df is None: raise HTTPException(status_code=404, detail=f"Dataset '{request.dataset_id}' not found.")
    
    try:
        # We derive the report by executing the autonomous pipeline once
        report_data = run_autonomous_analysis(df, request.dataset_id)
        pdf_path = generate_pdf_report(request.dataset_id, report_data)
        
        return {
            "report": pdf_path
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.drift_detection import detect_data_drift

class MonitorModelRequest(BaseModel):
    dataset_id: str
    new_dataset: str

@router.post("/monitor_model")
async def monitor_model_api(request: MonitorModelRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    df_train = get_user_dataset_df(db, request.dataset_id, current_user.id)
    df_new = get_user_dataset_df(db, request.new_dataset, current_user.id)
    
    if df_train is None:
        raise HTTPException(status_code=404, detail=f"Training dataset '{request.dataset_id}' not found.")
    if df_new is None:
        raise HTTPException(status_code=404, detail=f"New dataset '{request.new_dataset}' not found. Please upload it first.")
        
    try:
        drift_results = detect_data_drift(df_train, df_new, dataset_name=request.dataset_id)
        return drift_results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.agent_system import AgentManager

@router.get("/multi_agent_analysis")
async def multi_agent_analysis_api(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
    multi_agent_results = []
    for df, dataset_id in zip(dfs, ids):
        
        try:
            # Instantiate the coordinator agent manager
            manager = AgentManager(df)
            
            # Run the chained architecture
            report = manager.run_full_analysis()
            
            multi_agent_results.append({
                "dataset": dataset_id,
                "analysis_plan": report["plan"],
                "models": report["models"],
                "insights": report["insights"],
                "charts": report["charts"]
            })
        except Exception as e:
            import logging
            logging.error(f"Multi-Agent pipeline failed on {dataset_id}: {str(e)}")
            multi_agent_results.append({
                "dataset": dataset_id,
                "error": str(e)
            })
            
    if len(multi_agent_results) == 1:
        return multi_agent_results[0]
        
    return {"multi_agent_analysis": multi_agent_results}

from as_ai.memory_engine import load_analysis_history, save_feedback

@router.get("/ai_memory")
async def ai_memory_api():
    """
    Exposes the AI's Self-Learning historical memory summarizing total
    runs across different models recursively.
    """
    history = load_analysis_history()
    
    total = len(history)
    datasets = set()
    models_used = {}
    
    for record in history:
        datasets.add(record.get("dataset_name", "unknown"))
        model = record.get("best_model")
        if model:
            models_used[model] = models_used.get(model, 0) + 1
            
    return {
        "total_analyses": total,
        "best_models_used": models_used,
        "datasets_analyzed": list(datasets)
    }

class FeedbackRequest(BaseModel):
    analysis_id: str
    rating: int

@router.post("/analysis_feedback")
async def analysis_feedback_api(request: FeedbackRequest):
    """
    Ingests human feedback (rating 1-5) and links it directly to 
    an internal agent pipeline run, used dynamically to re-weight
    future ML recommendations locally.
    """
    try:
        # Constraint limits feedback to range 1-5
        rating = max(1, min(5, request.rating))
        save_feedback(request.analysis_id, rating)
        
        return {
            "message": f"Successfully mapped rating {rating} to {request.analysis_id}",
            "status": "success"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.streaming_engine import start_stream_consumer, get_stream_status

class StartStreamRequest(BaseModel):
    topic_name: str
    dataset_index: int = 0

@router.post("/start_stream")
async def start_stream_api(request: StartStreamRequest):
    """
    Initializes the Apache Kafka consumer listening loop appending live dictionaries 
    into active dataset variables dynamically tracked by the UI logic. 
    """
    try:
        response = start_stream_consumer(request.topic_name, DATASETS_STORE, request.dataset_index)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream_status")
async def stream_status_api():
    """
    Exposes processing loop tracking analytics continuously reporting anomaly distributions
    and last ingested record hashes.
    """
    try:
        return get_stream_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.story_engine import generate_data_story

@router.get("/executive_summary")
async def executive_summary_api(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dfs, ids = get_all_user_dfs(db, current_user.id)
    if not dfs: raise HTTPException(status_code=400, detail="No datasets uploaded.")
        
    try:
        story = generate_data_story()
        return {
            "title": "Dataset Executive Summary",
            "summary": story.get("summary", ""),
            "key_findings": story.get("key_drivers", []),
            "recommendations": story.get("recommendations", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.presentation_generator import generate_presentation

class PresentationRequest(BaseModel):
    dataset_id: str

@router.post("/generate_presentation")
async def generate_presentation_api(request: PresentationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    df = get_user_dataset_df(db, request.dataset_id, current_user.id)
    if df is None: raise HTTPException(status_code=404, detail="Dataset not found or no datasets uploaded.")
        
    try:
        # First generate the story content to populate slides
        story = generate_data_story()
        
        # Then generate the PPTX
        download_url = generate_presentation(request.dataset_id, story)
        
        return {
            "download_url": download_url
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.research_agent import ResearchAgent
from as_ai.ai_insights import detect_anomalies

@router.get("/research/hypotheses")
async def get_research_hypotheses():
    """
    Uses the AI Research Scientist to generate causal hypotheses from the dataset.
    Stores and returns them.
    """
    if not DATASETS_STORE:
        raise HTTPException(status_code=400, detail="No datasets uploaded.")
        
    try:
        df = DATASETS_STORE[0] # Using the first dataset for simplification
        dataset_name = "dataset_1"
        
        agent = ResearchAgent(dataset_name)
        
        # Build correlations and metrics
        numeric_df = df.select_dtypes(include=['number'])
        corr = {}
        if not numeric_df.empty and numeric_df.shape[1] > 1:
            try:
                corr_matrix = numeric_df.corr().unstack().sort_values(ascending=False).drop_duplicates()
                corr_matrix = corr_matrix[corr_matrix < 1] # Remove self correlation
                top_pairs = corr_matrix.head(5).to_dict()
                corr = {str(k): v for k, v in top_pairs.items()}
            except:
                pass
                
        stats = generate_dataset_insights(df)
        anomalies = detect_anomalies(df)
        
        # Generate and save
        new_hypotheses = agent.generate_hypotheses(stats, corr, anomalies)
        
        return {
            "dataset": dataset_name,
            "hypotheses": new_hypotheses.get("hypotheses", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.experiment_runner import ExperimentRunner

class RunExperimentRequest(BaseModel):
    dataset_id: str
    hypothesis: str

@router.post("/research/run_experiment")
async def run_experiment_api(request: RunExperimentRequest):
    """
    Autonomously executes statistical experiments to test generated hypotheses.
    Returns the results and matplotlib charts.
    """
    if not DATASETS_STORE:
        raise HTTPException(status_code=400, detail="No datasets uploaded.")
        
    try:
        df = DATASETS_STORE[0] # Usually map dynamically via dataset_id
        
        runner = ExperimentRunner(request.dataset_id)
        result = runner.run_experiment(request.hypothesis, df)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.research_paper_generator import ResearchPaperGenerator
import json

class GeneratePaperRequest(BaseModel):
    dataset_id: str

@router.post("/research/generate_paper")
async def generate_research_paper_api(request: GeneratePaperRequest):
    """
    Compiles generated hypotheses and experiment validations into a structured academic PDF.
    """
    if not DATASETS_STORE:
        raise HTTPException(status_code=400, detail="No datasets uploaded.")
        
    try:
        df = DATASETS_STORE[0]
        dataset_name = request.dataset_id
        
        profile = generate_dataset_insights(df)
        
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        hypotheses = []
        try:
            h_path = os.path.join(base_dir, "research", "hypotheses_history.json")
            with open(h_path, "r") as f:
                h_data = json.load(f)
                if h_data: hypotheses = h_data[-1].get("generated_hypotheses", [])
        except:
            pass
            
        experiments = []
        try:
            e_path = os.path.join(base_dir, "research", "experiments_history.json")
            with open(e_path, "r") as f:
                e_data = json.load(f)
                experiments = e_data[-3:] # Last 3 experiments logically fit on a small paper
        except:
            pass
            
        generator = ResearchPaperGenerator(dataset_name)
        result = generator.generate_research_paper(profile, hypotheses, experiments)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from as_ai.discovery_engine import DiscoveryEngine

class DiscoverPatternsRequest(BaseModel):
    dataset_id: str

@router.post("/research/discover_patterns")
async def discover_patterns_api(request: DiscoverPatternsRequest):
    """
    Autonomously analyzes the dataset to uncover structural patterns, clusters, and anomalies.
    Saves discoveries to history and outputs visualizations.
    """
    if not DATASETS_STORE:
        raise HTTPException(status_code=400, detail="No datasets uploaded.")
        
    try:
        df = DATASETS_STORE[0]
        
        engine = DiscoveryEngine(request.dataset_id)
        result = engine.discover_patterns(df)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
