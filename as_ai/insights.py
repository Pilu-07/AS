import pandas as pd
import numpy as np

def generate_dataset_insights(dataframe: pd.DataFrame) -> dict:
    """
    Computes and returns structural and statistical insights for a dataset.
    Includes row/col counts, missing values, and numeric/categorical summaries.
    """
    numeric_df = dataframe.select_dtypes(include='number')
    categorical_df = dataframe.select_dtypes(exclude='number')
    
    numeric_summary = {}
    if not numeric_df.empty:
        desc = numeric_df.describe().to_dict()
        for col, stats in desc.items():
            numeric_summary[col] = {
                "mean": stats.get("mean"),
                "median": stats.get("50%"),
                "min": stats.get("min"),
                "max": stats.get("max")
            }
            
    categorical_summary = {}
    for col in categorical_df.columns:
        counts = categorical_df[col].value_counts(dropna=False).head(10).to_dict()
        
        # Convert keys to str to ensure JSON serializability, handling NaN keys gracefully
        clean_counts = {}
        for k, v in counts.items():
            key_str = str(k) if pd.notna(k) else "NaN"
            clean_counts[key_str] = int(v)
            
        categorical_summary[col] = clean_counts
        
    missing_values = dataframe.isnull().sum().to_dict()
    
    return {
        "rows": int(dataframe.shape[0]),
        "columns": int(dataframe.shape[1]),
        "missing_values": {str(k): int(v) for k, v in missing_values.items()},
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary
    }
