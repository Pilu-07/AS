import os
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Safe for server environments without display
import matplotlib.pyplot as plt
import seaborn as sns

DASHBOARD_CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "dashboard")
os.makedirs(DASHBOARD_CHARTS_DIR, exist_ok=True)

def generate_dashboard(dataframe: pd.DataFrame, dataset_id: str) -> list[str]:
    """
    Automatically generates dashboard charts depending on column types:
    - Histogram and box plot for numeric columns.
    - Bar chart counts for categorical columns.
    - Correlation heatmap for datasets with multiple numeric columns.
    
    Returns a list of HTTP accessible chart paths.
    """
    chart_paths = []
    
    numeric_df = dataframe.select_dtypes(include='number')
    categorical_df = dataframe.select_dtypes(exclude='number')
    
    # 1. Numeric Distributions (Histograms & Box plots)
    for col in numeric_df.columns:
        # Histogram
        plt.figure(figsize=(8, 5))
        sns.histplot(dataframe[col].dropna(), kde=True)
        plt.title(f'Histogram of {col}')
        plt.tight_layout()
        hist_filename = f"dashboard_histogram_{dataset_id}_{col}.png"
        hist_filepath = os.path.join(DASHBOARD_CHARTS_DIR, hist_filename)
        plt.savefig(hist_filepath)
        plt.close()
        chart_paths.append(f"/charts/dashboard/{hist_filename}")
        
        # Boxplot
        plt.figure(figsize=(8, 5))
        sns.boxplot(x=dataframe[col].dropna())
        plt.title(f'Box Plot of {col}')
        plt.tight_layout()
        box_filename = f"dashboard_boxplot_{dataset_id}_{col}.png"
        box_filepath = os.path.join(DASHBOARD_CHARTS_DIR, box_filename)
        plt.savefig(box_filepath)
        plt.close()
        chart_paths.append(f"/charts/dashboard/{box_filename}")

    # 2. Categorical Counts (Bar Charts)
    for col in categorical_df.columns:
        # Prevent plotting columns with too many unique values (e.g., IDs)
        if dataframe[col].nunique() < 20:
            plt.figure(figsize=(8, 5))
            
            # Using countplot directly on the column
            sns.countplot(y=col, data=dataframe, order=dataframe[col].value_counts().index)
            plt.title(f'Count Plot of {col}')
            plt.tight_layout()
            
            bar_filename = f"dashboard_bar_{dataset_id}_{col}.png"
            bar_filepath = os.path.join(DASHBOARD_CHARTS_DIR, bar_filename)
            plt.savefig(bar_filepath)
            plt.close()
            chart_paths.append(f"/charts/dashboard/{bar_filename}")

    # 3. Correlation Heatmap
    if numeric_df.shape[1] > 1:
        plt.figure(figsize=(10, 8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Heatmap')
        plt.tight_layout()
        
        heatmap_filename = f"dashboard_heatmap_{dataset_id}.png"
        heatmap_filepath = os.path.join(DASHBOARD_CHARTS_DIR, heatmap_filename)
        plt.savefig(heatmap_filepath)
        plt.close()
        chart_paths.append(f"/charts/dashboard/{heatmap_filename}")

    return chart_paths
