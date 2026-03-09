import os
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

from as_ai.config import get_llm
from as_ai.insights import generate_dataset_insights
from as_ai.ai_insights import detect_anomalies, generate_ai_insights

AUTONOMOUS_CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "autonomous")
os.makedirs(AUTONOMOUS_CHARTS_DIR, exist_ok=True)

# Simple cache for autonomous analysis results to prevent recomputing
ANALYSIS_CACHE = {}

def get_analysis_plan(dataframe: pd.DataFrame, stats: Dict[str, Any]) -> dict:
    """Uses the LLM to generate an analysis plan based on dataset schema and statistics."""
    schema_cols = dataframe.columns.tolist()
    prompt = f"""
You are an expert data scientist. Given this dataset schema and statistics, decide what analyses should be performed.

Schema: {schema_cols}
Stats:
- Rows: {stats['rows']}
- Columns: {stats['columns']}

Return ONLY a valid JSON object matching exactly this structure:
{{
    "analysis_plan": [
        "distribution analysis",
        "correlation analysis",
        "outlier detection"
    ]
}}
"""
    llm = get_llm()
    
    if getattr(llm, "type", "unknown") == "fake":
        return {
            "analysis_plan": [
                "distribution analysis",
                "correlation analysis",
                "outlier detection",
                "feature importance"
            ]
        }
        
    try:
        from pandasai.core.prompts.base import BasePrompt
        class PlanPrompt(BasePrompt):
            def to_string(self) -> str:
                return prompt
                
        response = llm.call(PlanPrompt())
        response_text = response.replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)
    except Exception as e:
        return {
            "analysis_plan": [
                "distribution analysis",
                "correlation analysis"
            ]
        }

def generate_autonomous_visualizations(dataframe: pd.DataFrame, plan: dict, dataset_id: str) -> list[str]:
    """Generates visualizations based on the analysis plan."""
    chart_paths = []
    
    numeric_df = dataframe.select_dtypes(include='number')
    categorical_df = dataframe.select_dtypes(exclude='number')
    
    plan_steps = [step.lower() for step in plan.get("analysis_plan", [])]
    
    # 1. Distribution analysis => Histograms & Bar charts
    if any("distribution" in step for step in plan_steps):
        # Numeric histograms (limit to top 5 to avoid explosion)
        for col in list(numeric_df.columns)[:5]:
            plt.figure(figsize=(7, 4))
            sns.histplot(dataframe[col].dropna(), kde=True)
            plt.title(f'Distribution of {col}')
            plt.tight_layout()
            filename = f"autonomous_dist_{dataset_id}_{col}.png"
            filepath = os.path.join(AUTONOMOUS_CHARTS_DIR, filename)
            plt.savefig(filepath)
            plt.close()
            chart_paths.append(f"/charts/autonomous/{filename}")
            
        # Categorical bar charts (limit to top 3)
        for col in list(categorical_df.columns)[:3]:
            if dataframe[col].nunique() < 15:
                plt.figure(figsize=(7, 4))
                sns.countplot(y=col, data=dataframe, order=dataframe[col].value_counts().index)
                plt.title(f'Category Counts for {col}')
                plt.tight_layout()
                filename = f"autonomous_bar_{dataset_id}_{col}.png"
                filepath = os.path.join(AUTONOMOUS_CHARTS_DIR, filename)
                plt.savefig(filepath)
                plt.close()
                chart_paths.append(f"/charts/autonomous/{filename}")

    # 2. Correlation analysis => Heatmap
    if any("correlation" in step for step in plan_steps) and numeric_df.shape[1] > 1:
        plt.figure(figsize=(8, 6))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='RdBu_r', fmt=".2f")
        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        filename = f"autonomous_heatmap_{dataset_id}.png"
        filepath = os.path.join(AUTONOMOUS_CHARTS_DIR, filename)
        plt.savefig(filepath)
        plt.close()
        chart_paths.append(f"/charts/autonomous/{filename}")
        
    # 3. Time series analysis => Line chart (if date column exists)
    if any("time series" in step or "trend" in step for step in plan_steps):
        date_cols = [col for col in dataframe.columns if 'date' in col.lower() or 'time' in col.lower()]
        if date_cols and numeric_df.shape[1] > 0:
            date_col = date_cols[0]
            num_col = numeric_df.columns[0]
            try: # Attempt to plot if parsable
                df_time = dataframe[[date_col, num_col]].dropna().copy()
                df_time[date_col] = pd.to_datetime(df_time[date_col], errors='coerce')
                df_time = df_time.dropna().sort_values(by=date_col)
                if not df_time.empty:
                    plt.figure(figsize=(9, 4))
                    sns.lineplot(x=date_col, y=num_col, data=df_time)
                    plt.title(f'Trend of {num_col} over time')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    filename = f"autonomous_trend_{dataset_id}.png"
                    filepath = os.path.join(AUTONOMOUS_CHARTS_DIR, filename)
                    plt.savefig(filepath)
                    plt.close()
                    chart_paths.append(f"/charts/autonomous/{filename}")
            except Exception:
                pass

    return chart_paths

def run_autonomous_analysis(dataframe: pd.DataFrame, dataset_id: str) -> Dict[str, Any]:
    """
    Executes a fully autonomous step-by-step data analysis pipeline.
    Caches results to prevent recomputing heavy statistics on repeated requests.
    """
    # Simple caching mechanism (hash based on dataset_id and df shape)
    # Note: In production, consider hashing the dataframe contents or using an explicit cache invalidation
    cache_key = f"{dataset_id}_{dataframe.shape[0]}_{dataframe.shape[1]}"
    if cache_key in ANALYSIS_CACHE:
        return ANALYSIS_CACHE[cache_key]

    # 1 & 2 & 3. Profiling, Quality, Statistical Exploration
    stats = generate_dataset_insights(dataframe)
    
    # 4 & 5. Anomaly Detection
    anomalies = detect_anomalies(dataframe)
    
    # 6. Analysis Planner (LLM)
    plan = get_analysis_plan(dataframe, stats)
    
    # Auto Visualization Engine
    visualizations = generate_autonomous_visualizations(dataframe, plan, dataset_id)
    
    # 7. Insight Generation
    ai_insights = generate_ai_insights(dataframe)
    
    # Construct Full Report
    report = {
        "dataset_profile": stats,
        "analysis_plan": plan.get("analysis_plan", []),
        "visualizations": visualizations,
        "anomalies": anomalies,
        "insights": {
            "key_trends": ai_insights.get("key_trends"),
            "business_insights": ai_insights.get("business_insights")
        },
        "recommendations": ai_insights.get("recommended_visualizations", [])
    }
    
    # Save to cache
    ANALYSIS_CACHE[cache_key] = report
    
    return report
