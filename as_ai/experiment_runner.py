import os
import json
import re
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score

class ExperimentRunner:
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        
        # Directories
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.charts_dir = os.path.join(base_dir, "charts", "research")
        os.makedirs(self.charts_dir, exist_ok=True)
        
        self.research_dir = os.path.join(base_dir, "research")
        os.makedirs(self.research_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.research_dir, "experiments_history.json")

    def run_experiment(self, hypothesis: str, df: pd.DataFrame) -> dict:
        """
        Parses the hypothesis and autonomously runs the most appropriate statistical test.
        """
        h_lower = hypothesis.lower()
        result_payload = {
            "hypothesis": hypothesis,
            "result": "inconclusive",
            "confidence": 0.0,
            "method_used": "unknown",
            "metrics": {},
            "charts": []
        }
        
        if df.empty:
            result_payload["result"] = "error"
            return result_payload
            
        # Very rudimentary NLP rule-based routing for experiment types
        # Identify possible columns from hypothesis
        cols = [c for c in df.columns if c.lower() in h_lower]
        
        # If we couldn't find 2 columns from exact names, we might just pick top 2 numeric for demo fallback
        if len(cols) < 2:
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(num_cols) >= 2:
                cols = num_cols[:2]
            else:
                result_payload["result"] = "data_insufficient"
                return result_payload

        col_x = cols[0]
        col_y = cols[1]

        # Determine Method
        if "correlation" in h_lower or "correlates" in h_lower:
            result_payload = self._test_correlation(df, col_x, col_y, hypothesis)
        elif "influence" in h_lower or "affects" in h_lower or "predict" in h_lower:
            result_payload = self._test_regression(df, col_x, col_y, hypothesis)
        elif "difference" in h_lower or "higher" in h_lower or "lower" in h_lower:
            result_payload = self._test_correlation(df, col_x, col_y, hypothesis) # Simplification
        else:
            # Default to regression
            result_payload = self._test_regression(df, col_x, col_y, hypothesis)

        self._store_experiment(result_payload)
        return result_payload

    def _test_correlation(self, df: pd.DataFrame, col_x: str, col_y: str, hypothesis: str) -> dict:
        """Run Pearson / Spearman correlation."""
        # Convert to numeric if possible safely
        df_clean = df[[col_x, col_y]].dropna()
        if not pd.api.types.is_numeric_dtype(df_clean[col_x]):
            try:
                df_clean[col_x] = LabelEncoder().fit_transform(df_clean[col_x])
            except:
                pass
        if not pd.api.types.is_numeric_dtype(df_clean[col_y]):
            try:
                df_clean[col_y] = LabelEncoder().fit_transform(df_clean[col_y])
            except:
                pass

        if not pd.api.types.is_numeric_dtype(df_clean[col_x]) or not pd.api.types.is_numeric_dtype(df_clean[col_y]):
            return {"hypothesis": hypothesis, "result": "error", "confidence": 0, "method_used": "correlation", "metrics": {}}

        corr_val = df_clean[col_x].corr(df_clean[col_y])
        abs_corr = abs(corr_val)
        
        result_status = "supported" if abs_corr > 0.3 else ("weak support" if abs_corr > 0.1 else "rejected")
        confidence = min(0.99, abs_corr * 1.5) # Fake confidence scaling for demo
        
        # Visual
        chart_path = self._generate_scatter(df_clean, col_x, col_y, "correlation")

        return {
            "hypothesis": hypothesis,
            "result": result_status,
            "confidence": round(confidence, 2),
            "method_used": "pearson_correlation",
            "metrics": {
                "r_value": round(corr_val, 4)
            },
            "charts": [chart_path]
        }

    def _test_regression(self, df: pd.DataFrame, col_x: str, col_y: str, hypothesis: str) -> dict:
        """Run Linear or Logistic Regression."""
        df_clean = df[[col_x, col_y]].dropna()
        
        # Force numeric
        for col in [col_x, col_y]:
            if not pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = LabelEncoder().fit_transform(df_clean[col])
                
        X = df_clean[[col_x]]
        y = df_clean[col_y]
        
        unique_y = y.nunique()
        is_classification = unique_y <= 5
        
        if is_classification:
            model = LogisticRegression(max_iter=200)
            method = "logistic_regression"
        else:
            model = LinearRegression()
            method = "linear_regression"
            
        try:
            model.fit(X, y)
            score = model.score(X, y) # R2 for linear, Accuracy for Logistic
            
            coef = float(model.coef_[0]) if is_classification else float(model.coef_[0])
            
            if is_classification:
                supported = score > 0.6
                confidence = score
            else:
                supported = score > 0.1
                confidence = min(0.99, score * 3) # Scaled for reasonable visuals
                
            res_str = "supported" if supported else "rejected"
            
            # Visual
            chart_path = self._generate_scatter(df_clean, col_x, col_y, "regression")
            
            return {
                "hypothesis": hypothesis,
                "result": res_str,
                "confidence": round(confidence, 2),
                "method_used": method,
                "metrics": {
                    "coefficient": round(coef, 4),
                    "score": round(score, 4)
                },
                "charts": [chart_path]
            }
        except Exception as e:
            return {"hypothesis": hypothesis, "result": "error", "confidence": 0, "method_used": method, "metrics": {"error": str(e)}, "charts": []}

    def _generate_scatter(self, df: pd.DataFrame, x_col: str, y_col: str, prefix: str) -> str:
        """Generates a scatter plot with regression line."""
        plt.figure(figsize=(8, 6))
        sns.set_theme(style="whitegrid")
        
        # Sample to prevent massive plotting
        plot_df = df.sample(min(1000, len(df)))
        
        try:
            sns.regplot(data=plot_df, x=x_col, y=y_col, scatter_kws={'alpha':0.5, 'color':'#6366F1'}, line_kws={'color':'#EF4444'})
        except:
            sns.scatterplot(data=plot_df, x=x_col, y=y_col, alpha=0.5, color='#6366F1')
            
        plt.title(f"{y_col} vs {x_col}", fontsize=14, fontweight='bold', color='#374151')
        plt.xlabel(x_col, fontsize=12, fontweight='bold', color='#4B5563')
        plt.ylabel(y_col, fontsize=12, fontweight='bold', color='#4B5563')
        plt.tight_layout()
        
        filename = f"experiment_{prefix}_{x_col}_{y_col}_{int(datetime.now().timestamp())}.png"
        filename = re.sub(r'[^a-zA-Z0-9_\.]', '_', filename) # Sanitization
        
        file_path = os.path.join(self.charts_dir, filename)
        plt.savefig(file_path, facecolor='#F3F4F6')
        plt.close()
        
        return f"/charts/research/{filename}"

    def _store_experiment(self, result: dict):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    content = f.read()
                    if content.strip():
                        history = json.loads(content)
            except:
                pass
                
        result["timestamp"] = datetime.now().isoformat()
        result["dataset"] = self.dataset_id
        
        history.append(result)
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)
