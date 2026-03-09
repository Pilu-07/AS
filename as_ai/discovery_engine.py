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
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class DiscoveryEngine:
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        
        # Directories
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.charts_dir = os.path.join(self.base_dir, "charts", "discovery")
        os.makedirs(self.charts_dir, exist_ok=True)
        
        self.research_dir = os.path.join(self.base_dir, "research")
        os.makedirs(self.research_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.research_dir, "discoveries_history.json")

    def discover_patterns(self, df: pd.DataFrame) -> dict:
        """
        Runs unsupervised learning algorithms to find dataset patterns natively.
        Returns cluster, anomaly, and trend discoveries.
        """
        discoveries = []
        charts = []
        
        if df.empty:
            return {"dataset": self.dataset_id, "discoveries": [], "charts": []}

        numeric_df = df.select_dtypes(include=['number']).dropna()
        if numeric_df.empty or numeric_df.shape[1] < 2:
            return {"dataset": self.dataset_id, "discoveries": [], "charts": []}

        # Subsample for speed if huge
        if len(numeric_df) > 5000:
            numeric_df = numeric_df.sample(5000, random_state=42)
            
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df)

        # 1. Clustering Analysis (KMeans + PCA for visual)
        try:
            n_clusters = min(3, len(numeric_df))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_data)
            
            pca = PCA(n_components=2)
            pca_data = pca.fit_transform(scaled_data)
            
            # Generate Cluster Visual
            plt.figure(figsize=(8, 6))
            sns.scatterplot(x=pca_data[:, 0], y=pca_data[:, 1], hue=clusters, palette="viridis", alpha=0.7)
            plt.title("PCA Projection: Discovered Clusters", fontsize=14, fontweight='bold', color='#374151')
            plt.xlabel("Principal Component 1", fontweight='bold')
            plt.ylabel("Principal Component 2", fontweight='bold')
            
            cluster_chart_path = self._save_chart("cluster_pca")
            charts.append(cluster_chart_path)
            
            # Identify most defining features per cluster (heuristic)
            centers = scaler.inverse_transform(kmeans.cluster_centers_)
            defining_features = []
            for i, col in enumerate(numeric_df.columns[:2]): # Top 2 numeric for description
                diffs = [abs(centers[c][i] - centers[(c+1)%n_clusters][i]) for c in range(n_clusters)]
                if sum(diffs) > 0:
                    defining_features.append(col)
                    
            desc = f"Data naturally splits into {n_clusters} distinct groups."
            if defining_features:
                desc += f" Primarily differentiated by variations in {', '.join(defining_features)}."
                
            discoveries.append({
                "type": "cluster_pattern",
                "description": desc
            })
        except Exception as e:
            pass

        # 2. Anomaly Detection (Isolation Forest)
        try:
            iso = IsolationForest(contamination=0.05, random_state=42)
            anomalies = iso.fit_predict(scaled_data)
            outlier_pct = round((sum(anomalies == -1) / len(anomalies)) * 100, 2)
            
            if outlier_pct > 0:
                # Find column with highest deviance in outliers vs normal
                outlier_idx = np.where(anomalies == -1)[0]
                normal_idx = np.where(anomalies == 1)[0]
                
                if len(outlier_idx) > 0 and len(normal_idx) > 0:
                    outliers_df = numeric_df.iloc[outlier_idx]
                    normals_df = numeric_df.iloc[normal_idx]
                    
                    diff = abs(outliers_df.mean() - normals_df.mean()) / normals_df.std()
                    top_anomaly_col = diff.idxmax()
                    
                    discoveries.append({
                        "type": "anomaly_pattern",
                        "description": f"Detected {outlier_pct}% structural anomalies. Extreme deviations observed heavily in '{top_anomaly_col}'."
                    })
        except Exception as e:
            pass

        # 3. Correlation / Linear Trends
        try:
            corr = numeric_df.corr()
            np.fill_diagonal(corr.values, 0)
            max_corr = corr.unstack().idxmax()
            min_corr = corr.unstack().idxmin() # Negative correlation
            
            if abs(corr.loc[max_corr[0], max_corr[1]]) > 0.5:
                discoveries.append({
                    "type": "trend_pattern",
                    "description": f"Strong positive correlation ({round(corr.loc[max_corr[0], max_corr[1]], 2)}) discovered between '{max_corr[0]}' and '{max_corr[1]}'."
                })
                
                # Plot this trend
                plt.figure(figsize=(8, 6))
                sns.regplot(data=numeric_df, x=max_corr[0], y=max_corr[1], scatter_kws={'alpha':0.4, 'color':'#10B981'}, line_kws={'color':'#3B82F6'})
                plt.title(f"Discovered Pattern: {max_corr[0]} vs {max_corr[1]}", fontsize=14, fontweight='bold', color='#374151')
                trend_chart_path = self._save_chart(f"trend_{max_corr[0][:5]}_{max_corr[1][:5]}")
                charts.append(trend_chart_path)
                
        except Exception as e:
            pass

        result_payload = {
            "dataset": self.dataset_id,
            "discoveries": discoveries,
            "charts": charts,
            "timestamp": datetime.now().isoformat()
        }

        self._store_discovery(result_payload)
        return result_payload

    def _save_chart(self, prefix: str) -> str:
        filename = f"discovery_{prefix}_{int(datetime.now().timestamp())}.png"
        filename = re.sub(r'[^a-zA-Z0-9_\.]', '_', filename)
        
        file_path = os.path.join(self.charts_dir, filename)
        plt.tight_layout()
        plt.savefig(file_path, facecolor='#F3F4F6')
        plt.close()
        return f"/charts/discovery/{filename}"

    def _store_discovery(self, result: dict):
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    content = f.read()
                    if content.strip():
                        history = json.loads(content)
            except:
                pass
                
        history.append(result)
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)
