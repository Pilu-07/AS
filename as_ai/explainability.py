import os
import time
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from typing import Dict, Any

CHARTS_MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "models")
os.makedirs(CHARTS_MODELS_DIR, exist_ok=True)

def generate_shap_explanations(model_obj: Any, X_train: Any, dataset_id: str, target: str) -> Dict[str, str]:
    """
    Uses SHAP to generate explainability plots for model predictions.
    Supports TreeExplainer models like RandomForest and XGBoost.
    Returns the paths to the generated charts.
    """
    charts = {}
    
    # SHAP currently supports tree-based models best out-of-the-box
    model_name = type(model_obj).__name__
    if 'RandomForest' in model_name or 'XGB' in model_name:
        try:
            # We sample X_train if it's too large to keep explanation fast
            if X_train.shape[0] > 1000:
                X_sample = shap.sample(X_train, 1000)
            else:
                X_sample = X_train
                
            explainer = shap.TreeExplainer(model_obj)
            shap_values = explainer.shap_values(X_sample)
            
            # Handle multi-class classification shap values structurally (list of arrays vs array)
            if isinstance(shap_values, list):
                # Just plot for class 0 for simplicity in macro reports
                plot_vals = shap_values[0]
            else:
                plot_vals = shap_values
            
            timestamp = int(time.time())
            
            # 1. Summary Plot
            plt.figure(figsize=(10, 6))
            shap.summary_plot(plot_vals, X_sample, show=False)
            plt.title(f'SHAP Summary ({target})')
            plt.tight_layout()
            
            summary_filename = f"shap_summary_{dataset_id}_{target}_{timestamp}.png"
            summary_filepath = os.path.join(CHARTS_MODELS_DIR, summary_filename)
            plt.savefig(summary_filepath, bbox_inches='tight')
            plt.close()
            charts['shap_summary'] = f"/charts/models/{summary_filename}"
            
            # 2. Dependence Plot (use the first feature for simplicity)
            if X_sample.shape[1] > 0:
                top_feature = X_sample.columns[0]
                plt.figure(figsize=(8, 5))
                shap.dependence_plot(top_feature, plot_vals, X_sample, show=False)
                plt.title(f'SHAP Dependence Plot: {top_feature}')
                plt.tight_layout()
                
                dep_filename = f"shap_dependence_{dataset_id}_{target}_{timestamp}.png"
                dep_filepath = os.path.join(CHARTS_MODELS_DIR, dep_filename)
                plt.savefig(dep_filepath, bbox_inches='tight')
                plt.close()
                charts['shap_dependence'] = f"/charts/models/{dep_filename}"
                
        except Exception as e:
            # Catch SHAP exceptions (e.g., incompatible model structures) gracefully
            import logging
            logging.error(f"SHAP Explainer failed: {str(e)}")
            
    return charts
