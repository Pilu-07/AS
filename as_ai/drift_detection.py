import os
import time
import logging
import pandas as pd
from scipy.stats import ks_2samp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

CHARTS_DRIFT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "drift")
os.makedirs(CHARTS_DRIFT_DIR, exist_ok=True)

# Set up dedicated drift logger
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)
drift_logger = logging.getLogger("drift_logger")
drift_logger.setLevel(logging.INFO)
fh = logging.FileHandler(os.path.join(log_dir, "drift_logs.txt"))
fh.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d'))
drift_logger.addHandler(fh)

def plot_drift_comparison(train_series: pd.Series, new_series: pd.Series, column_name: str) -> str:
    """
    Generates a seaborn KDE plot overlaying the training distribution and new data distribution.
    Saves to /charts/drift/
    """
    plt.figure(figsize=(8, 5))
    sns.kdeplot(train_series.dropna(), label='Training Data', fill=True, alpha=0.5, color='blue')
    sns.kdeplot(new_series.dropna(), label='New Data', fill=True, alpha=0.5, color='red')
    
    plt.title(f'Data Drift Comparison: {column_name}')
    plt.legend()
    plt.tight_layout()
    
    filename = f"drift_comparison_{column_name}_{int(time.time())}.png"
    filepath = os.path.join(CHARTS_DRIFT_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    
    return f"/charts/drift/{filename}"

def detect_data_drift(train_df: pd.DataFrame, new_df: pd.DataFrame, dataset_name: str = "dataset") -> Dict[str, Any]:
    """
    Detects statistical drift between a training dataset and a new incoming dataset.
    Uses Kolmogorov-Smirnov test (ks_2samp) for all intersecting numeric columns.
    Generates KDE plot visualizations for drifted features.
    """
    drifted_features = []
    p_values = {}
    drift_charts = []
    
    # Identify numeric columns present in both datasets
    train_numeric = train_df.select_dtypes(include='number').columns
    new_numeric = new_df.select_dtypes(include='number').columns
    common_cols = set(train_numeric).intersection(new_numeric)
    
    for col in common_cols:
        train_data = train_df[col].dropna()
        new_data = new_df[col].dropna()
        
        if len(train_data) == 0 or len(new_data) == 0:
            continue
            
        # Kolmogorov-Smirnov test
        stat, p_value = ks_2samp(train_data, new_data)
        
        # If p-value < 0.05, distributions are significantly different
        if p_value < 0.05:
            drifted_features.append(col)
            p_values[col] = float(p_value)
            
            # Generate visualization
            chart_path = plot_drift_comparison(train_data, new_data, col)
            drift_charts.append(chart_path)
            
    drift_detected = len(drifted_features) > 0
    
    # Log the outcome
    if drift_detected:
        features_str = ", ".join(drifted_features)
        drift_logger.info(f"{dataset_name} | drift detected in {features_str}")
    else:
        drift_logger.info(f"{dataset_name} | no drift detected")
        
    return {
        "drift_detected": drift_detected,
        "drifted_features": drifted_features,
        "p_values": p_values,
        "drift_charts": drift_charts
    }
