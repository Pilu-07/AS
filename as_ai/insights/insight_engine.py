import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from as_ai.database.models import Dataset, DatasetInsight, get_db
from as_ai.dataset_loader import load_dataset
from as_ai.llm_pipeline import generate_text
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.impute import SimpleImputer
import logging

logger = logging.getLogger(__name__)

def generate_human_explanation(insight_type: str, raw_findings: str) -> str:
    """
    Uses the LLM to rewrite technical data findings into a human-readable business insight.
    """
    prompt = f"""You are an expert Data Analyst reporting findings to an executive.
I have detected the following statistical pattern inside a dataset:
---
Type: {insight_type}
Technical Findings: {raw_findings}
---
Write a single, concise, professional sentence summarizing this insight in plain English. 
Do not use technical jargon or mention the code/statistics unless absolutely necessary.
Example: "Advertising budget increases appear strongly associated with revenue growth."
"""
    try:
        explanation = generate_text(prompt).strip()
        return explanation
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        return raw_findings

def analyze_correlations(df: pd.DataFrame) -> list:
    insights = []
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return insights
    
    corr_matrix = numeric_df.corr().abs()
    
    # Get upper triangle
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    # Find strong correlations (> 0.75)
    for col in upper.columns:
        for row in upper.index:
            val = upper.loc[row, col]
            if pd.notna(val) and val > 0.75:
                raw_text = f"{col} and {row} have a high correlation of {val:.2f}"
                explanation = generate_human_explanation("correlation", raw_text)
                insights.append({
                    "type": "correlation",
                    "description": explanation,
                    "importance": min(val + 0.1, 1.0) # Scale importance by correlation strength
                })
    return insights

def analyze_outliers(df: pd.DataFrame) -> list:
    insights = []
    numeric_df = df.select_dtypes(include=[np.number])
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if len(series) < 10:
            continue
            
        mean = series.mean()
        std = series.std()
        if std == 0: continue
        
        z_scores = ((series - mean) / std).abs()
        outliers = z_scores[z_scores > 3]
        
        if len(outliers) > 0:
            outlier_pct = len(outliers) / len(series) * 100
            if outlier_pct < 5: # If more than 5%, it's just a skewed distribution
                raw_text = f"Column '{col}' contains {len(outliers)} significant outliers ({outlier_pct:.1f}% of data)."
                explanation = generate_human_explanation("outlier_detection", raw_text)
                insights.append({
                    "type": "outlier",
                    "description": explanation,
                    "importance": min(0.6 + outlier_pct / 10, 0.95)
                })
    return insights

def analyze_feature_importance(df: pd.DataFrame) -> list:
    insights = []
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.shape[1] < 3:
        return insights
        
    # Pick the most "predictable" looking column (often the last one, or one with many unique values)
    # For a generic insight, we'll try predicting the column with the highest variance
    variances = numeric_df.var()
    target_col = variances.idxmax()
    
    if pd.isna(target_col): return insights
    
    X = numeric_df.drop(columns=[target_col])
    y = numeric_df[target_col]
    
    # Impute missing values
    imputer = SimpleImputer(strategy='mean')
    try:
        X_imputed = imputer.fit_transform(X)
        y_imputed = y.fillna(y.mean())
        
        # We assume regression for highest variance numerical col
        model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        model.fit(X_imputed, y_imputed)
        
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        top_feature = X.columns[indices[0]]
        top_importance = importances[indices[0]]
        
        if top_importance > 0.3: # Only report if a feature is highly dominant
            raw_text = f"Feature '{top_feature}' is the strongest predictor for '{target_col}' with an importance score of {top_importance:.2f}."
            explanation = generate_human_explanation("feature_importance", raw_text)
            insights.append({
                "type": "feature_importance",
                "description": explanation,
                "importance": top_importance
            })
    except Exception as e:
        logger.error(f"Error in feature importance insight: {e}")
        pass
        
    return insights

def analyze_dataset_insights(dataset_id: int):
    """
    Main driver method to run all insight jobs over a dataset id.
    Called asynchronously from background processing.
    """
    # Create DB session explicitly since this runs in a background thread
    from as_ai.database.models import SessionLocal
    db = SessionLocal()
    
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found for insight generation.")
            return

        df = load_dataset(dataset.file_path)
        if df is None or df.empty:
            logger.error(f"Dataset {dataset_id} failed to load or is empty.")
            return
            
        # Run analytical passes
        all_insights = []
        all_insights.extend(analyze_correlations(df))
        all_insights.extend(analyze_outliers(df))
        all_insights.extend(analyze_feature_importance(df))
        
        # Sort by importance and take top 10 to avoid noise
        all_insights = sorted(all_insights, key=lambda x: x["importance"], reverse=True)[:10]
        
        # Save to DB
        # First clear out any old insights if re-running
        db.query(DatasetInsight).filter(DatasetInsight.dataset_id == dataset_id).delete()
        
        for ins in all_insights:
            db_insight = DatasetInsight(
                dataset_id=dataset_id,
                insight_type=ins["type"],
                description=ins["description"],
                importance_score=ins["importance"]
            )
            db.add(db_insight)
            
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to generate insights for dataset {dataset_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
