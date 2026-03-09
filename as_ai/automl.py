import os
import time
import json
import logging
from typing import Dict, Any

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

# Global Cache to prevent retraining
MODEL_CACHE = {}

# Set up dedicated AutoML logger
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "training_logs.txt"),
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

CHARTS_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "models")
os.makedirs(CHARTS_MODELS_DIR, exist_ok=True)


def determine_task_type(series: pd.Series) -> str:
    """Detects if the target is for classification or regression."""
    if series.dtype == 'object' or pd.api.types.is_categorical_dtype(series):
        return 'classification'
    elif series.nunique() < 20: 
        # Even numerical columns might be classification if cardinality is low
        return 'classification'
    else:
        return 'regression'


def plot_feature_importance(importance_dict: dict, dataset_id: str, target_column: str) -> str:
    """Generates and saves a top 10 feature importance bar chart."""
    if not importance_dict:
        return None
        
    df_imp = pd.DataFrame(list(importance_dict.items()), columns=['Feature', 'Importance'])
    df_imp = df_imp.sort_values(by='Importance', ascending=False).head(10)
    
    plt.figure(figsize=(8, 5))
    sns.barplot(x='Importance', y='Feature', data=df_imp, palette='viridis')
    plt.title(f'Top 10 Feature Importances (Target: {target_column})')
    plt.tight_layout()
    
    filename = f"feature_importance_{dataset_id}_{target_column}_{int(time.time())}.png"
    filepath = os.path.join(CHARTS_MODELS_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return f"/charts/models/{filename}"


def train_best_model(df: pd.DataFrame, target_column: str, dataset_id: str = "dataset") -> Dict[str, Any]:
    """
    AutoML Engine: Detects task, trains models, evaluates metrics, and returns the best model details.
    Uses caching to prevent retraining the same dataset+target combination.
    """
    cache_key = f"{dataset_id}_{target_column}"
    if cache_key in MODEL_CACHE:
        logging.info(f"Retrieved cached model for {cache_key}")
        return MODEL_CACHE[cache_key]
        
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")

    # Drop rows where target is missing
    ml_df = df.dropna(subset=[target_column]).copy()
    
    # Simple preprocessing: drop columns with too many missing values, fill others with median/mode
    ml_df = ml_df.dropna(thresh=int(0.7*len(ml_df)), axis=1)
    
    numeric_cols = ml_df.select_dtypes(include='number').columns
    categorical_cols = ml_df.select_dtypes(exclude='number').columns
    
    for col in numeric_cols:
        ml_df[col] = ml_df[col].fillna(ml_df[col].median())
    for col in categorical_cols:
        if col != target_column:
            ml_df[col] = ml_df[col].fillna(ml_df[col].mode()[0] if not ml_df[col].mode().empty else "Unknown")
            
    task_type = determine_task_type(ml_df[target_column])
    
    # Label encode target if classification
    label_encoder = None
    y_full = ml_df[target_column]
    if task_type == 'classification' and y_full.dtype == 'object':
        label_encoder = LabelEncoder()
        y_full = label_encoder.fit_transform(y_full)
    
    # One-hot encode features
    X_full = ml_df.drop(columns=[target_column])
    X_full = pd.get_dummies(X_full, drop_first=True)
    
    # Ensure X only has numeric data after get_dummies
    X_full = X_full.select_dtypes(include='number')
    
    X_train, X_test, y_train, y_test = train_test_split(X_full, y_full, test_size=0.2, random_state=42)
    
    best_model_name = ""
    best_model_obj = None
    best_metrics = {}
    best_score = -float('inf') if task_type == 'classification' else float('inf')
    
    feature_importances = {}

    if task_type == 'classification':
        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000),
            "RandomForestClassifier": RandomForestClassifier(random_state=42),
            "XGBoostClassifier": XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        }
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                # Use macro average to support multi-class natively
                metrics = {
                    "accuracy": accuracy_score(y_test, preds),
                    "precision": precision_score(y_test, preds, average='macro', zero_division=0),
                    "recall": recall_score(y_test, preds, average='macro', zero_division=0),
                    "f1_score": f1_score(y_test, preds, average='macro', zero_division=0)
                }
                
                # Maximize F1 score
                score = metrics['f1_score']
                if score > best_score:
                    best_score = score
                    best_model_name = name
                    best_metrics = metrics
                    best_model_obj = model
            except Exception as e:
                logging.error(f"Failed to train {name}: {str(e)}")
                continue

    else: # regression
        models = {
            "LinearRegression": LinearRegression(),
            "RandomForestRegressor": RandomForestRegressor(random_state=42),
            "XGBoostRegressor": XGBRegressor(random_state=42)
        }
        
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                
                metrics = {
                    "rmse": mean_squared_error(y_test, preds, squared=False),
                    "r2": r2_score(y_test, preds)
                }
                
                # Minimize RMSE
                score = metrics['rmse']
                if score < best_score:
                    best_score = score
                    best_model_name = name
                    best_metrics = metrics
                    best_model_obj = model
            except Exception as e:
                logging.error(f"Failed to train {name}: {str(e)}")
                continue

    if best_model_obj is None:
        raise RuntimeError("No models could be successfully trained on this dataset.")

    # Extract Feature Importances
    if hasattr(best_model_obj, 'feature_importances_'):
        importance_vals = best_model_obj.feature_importances_
        feature_importances = dict(zip(X_full.columns, importance_vals))
    elif hasattr(best_model_obj, 'coef_'):
        # For Linear/Logistic Regression, use absolute coefficients
        importance_vals = abs(best_model_obj.coef_[0]) if len(best_model_obj.coef_.shape) > 1 else abs(best_model_obj.coef_)
        feature_importances = dict(zip(X_full.columns, importance_vals))
        
    # Convert numpy types to python native types for JSON serialization
    feature_importances = {str(k): float(v) for k, v in feature_importances.items()}
    best_metrics = {str(k): float(v) for k, v in best_metrics.items()}
        
    chart_path = plot_feature_importance(feature_importances, dataset_id, target_column)
    
    result = {
        "best_model": best_model_name,
        "task_type": task_type,
        "metrics": best_metrics,
        "feature_importance": feature_importances,
        "feature_importance_chart": chart_path,
        "model_obj": best_model_obj, # Save in cache but don't return to API directly
        "X_train": X_train           # Needed downstream for SHAP
    }
    
    import datetime
    MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    metadata = {
        "dataset_id": dataset_id,
        "target_column": target_column,
        "model": best_model_name,
        "train_rows": int(len(ml_df)),
        "features": list(X_full.columns),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d")
    }
    
    meta_path = os.path.join(MODELS_DIR, f"model_metadata_{dataset_id}.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)
        
    MODEL_CACHE[cache_key] = result
    
    logging.info(f"Trained AutoML: dataset={dataset_id}, target={target_column}, best_model={best_model_name}, metrics={json.dumps(best_metrics)}")
    
    return result
