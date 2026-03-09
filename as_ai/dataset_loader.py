import pandas as pd
import os

def load_dataset(file_path: str) -> pd.DataFrame:
    """Loads a dataset from CSV or Excel and returns a pandas DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only CSV and Excel are supported.")

def get_schema(dataframe: pd.DataFrame) -> dict:
    """Returns the schema of the provided DataFrame."""
    return {
        "columns": dataframe.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in dataframe.dtypes.items()},
        "sample_rows": dataframe.head(5).to_dict(orient="records")
    }
