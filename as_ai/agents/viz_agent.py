import os
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List

CHARTS_AGENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "charts", "agents")
os.makedirs(CHARTS_AGENTS_DIR, exist_ok=True)

class VisualizationAgent:
    """
    Generates core visual analytics charts automatically 
    (Distributions, Correlation Heatmaps, Scatter matrices).
    """
    
    def generate_visualizations(self, dataframe: pd.DataFrame) -> List[str]:
        charts = []
        numeric_df = dataframe.select_dtypes(include='number')
        timestamp = int(time.time())
        
        # 1. Distributions (Top 2 Numeric)
        for col in list(numeric_df.columns)[:2]:
            plt.figure(figsize=(7, 4))
            sns.histplot(dataframe[col].dropna(), kde=True, color='teal')
            plt.title(f'Distribution of {col}')
            plt.tight_layout()
            
            filename = f"distribution_{col}_{timestamp}.png"
            filepath = os.path.join(CHARTS_AGENTS_DIR, filename)
            plt.savefig(filepath)
            plt.close()
            charts.append(f"/charts/agents/{filename}")
            
        # 2. Correlation Heatmap
        if numeric_df.shape[1] > 1:
            plt.figure(figsize=(8, 6))
            corr = numeric_df.corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
            plt.title('Feature Correlation Heatmap')
            plt.tight_layout()
            
            filename = f"correlation_heatmap_{timestamp}.png"
            filepath = os.path.join(CHARTS_AGENTS_DIR, filename)
            plt.savefig(filepath)
            plt.close()
            charts.append(f"/charts/agents/{filename}")
            
        return charts
