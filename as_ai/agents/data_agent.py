import pandas as pd
import numpy as np
import logging

class DataAgent:
    """
    Responsible for automatically fixing dataset issues including 
    missing values, duplicate rows, checking datatypes, and outlier clipping.
    """
    
    def clean_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        
        # 1. Remove obvious duplicates
        start_rows = len(df)
        df = df.drop_duplicates()
        dropped_dups = start_rows - len(df)
        if dropped_dups > 0:
            logging.info(f"DataAgent: Removed {dropped_dups} duplicate rows.")
            
        numeric_cols = df.select_dtypes(include='number').columns
        categorical_cols = df.select_dtypes(exclude='number').columns
        
        # 2. Convert apparent date columns
        for col in categorical_cols:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    logging.info(f"DataAgent: Converted {col} to datetime.")
                except Exception:
                    pass
        
        # Re-fetch categoricals in case dates changed
        categorical_cols = df.select_dtypes(exclude=['number', 'datetime']).columns
        
        # 3. Fill Numeric NaNs with median
        for col in numeric_cols:
            if df[col].isnull().any():
                med = df[col].median()
                df[col] = df[col].fillna(med)
                
        # 4. Fill Categorical NaNs with mode
        for col in categorical_cols:
            if df[col].isnull().any():
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                else:
                    df[col] = df[col].fillna("Unknown")
                    
        # 5. Outlier Clipping (Clip to 1st and 99th percentiles)
        for col in numeric_cols:
            q_low = df[col].quantile(0.01)
            q_high = df[col].quantile(0.99)
            if pd.notna(q_low) and pd.notna(q_high):
                df[col] = df[col].clip(lower=q_low, upper=q_high)
                
        return df
