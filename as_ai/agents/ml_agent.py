import pandas as pd
import logging
from typing import Dict, Any

from as_ai.automl import train_best_model
from as_ai.memory_engine import recommend_model, save_analysis_result

class MLAgent:
    """
    Responsible for executing the AutoML engine over cleaned datasets
    and evaluating the results. Integrates with the Self-Learning Memory Engine.
    """
    
    def train_models(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        if dataframe.empty or dataframe.shape[1] < 2:
            return {"error": "Dataset too small for ML."}
            
        potential_targets = dataframe.columns.tolist()[::-1]
        
        target_col = None
        for col in potential_targets:
            if dataframe[col].nunique() < 20 or dataframe[col].dtype == 'object':
                target_col = col
                break
                
        if not target_col:
            target_col = potential_targets[0]
            
        logging.info(f"MLAgent: Guessed target column '{target_col}'")
        
        # 1. Ask Memory Engine for a recommendation first
        historical_recommendation = recommend_model(dataframe.columns.tolist(), target_col)
        if historical_recommendation:
            logging.info(f"MLAgent: Memory Engine recommended model '{historical_recommendation}' based on past experience.")
        
        try:
            # 2. Train AutoML
            result = train_best_model(dataframe, target_col, dataset_id="agent_run")
            
            best_model = result.get("best_model")
            
            # 3. Save memory context loop
            metrics = result.get("metrics", {})
            f1 = metrics.get("f1_score", 0.0)
            r2 = metrics.get("r2", 0.0)
            
            feat_imp = result.get("feature_importance", {})
            top_features = list(feat_imp.keys())[:5]
            
            memory_record = {
                "dataset_name": "agent_run",
                "target_column": target_col,
                "best_model": best_model,
                "f1_score": f1,
                "r2_score": r2,
                "top_features": top_features,
                "features": dataframe.columns.tolist()
            }
            analysis_id = save_analysis_result(memory_record)
            
            return {
                "target_column": target_col,
                "best_model": best_model,
                "historical_recommendation": historical_recommendation,
                "analysis_id": analysis_id,
                "task_type": result.get("task_type"),
                "metrics": metrics,
                "feature_importance": feat_imp,
                "feature_importance_chart": result.get("feature_importance_chart")
            }
        except Exception as e:
            logging.error(f"MLAgent Error: {str(e)}")
            return {"error": str(e)}
