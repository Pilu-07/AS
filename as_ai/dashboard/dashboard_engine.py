import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_dashboard(dataset_id: int):
    """
    Analyzes a dataset schema, extracts KPIs, designs chart configurations,
    and stores the JSON payload in the database.
    """
    from as_ai.database.models import SessionLocal, Dataset, DatasetDashboard
    from as_ai.dataset_loader import load_dataset
    
    db = SessionLocal()
    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found for dashboard gen.")
            return
            
        df = load_dataset(dataset.file_path)
        if df is None or df.empty:
            logger.error(f"Dataset {dataset_id} failed to load or is empty.")
            return

        # 1. Schema Analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        
        # Fallback date detection
        if not datetime_cols:
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower() or 'timestamp' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                        datetime_cols.append(col)
                        if col in categorical_cols: categorical_cols.remove(col)
                        if col in numeric_cols: numeric_cols.remove(col)
                    except:
                        pass

        # 2. Extract KPIs
        kpis = [
            {"label": "Total Rows", "value": f"{len(df):,}"},
            {"label": "Total Features", "value": f"{len(df.columns)}"}
        ]
        
        # Top Category KPI
        if categorical_cols:
            top_cat_col = categorical_cols[0]
            try:
                biggest_cat = df[top_cat_col].value_counts().idxmax()
                kpis.append({"label": f"Top {top_cat_col}", "value": str(biggest_cat)})
            except:
                pass
                
        # Average Numeric KPI
        if numeric_cols:
            metric_col = numeric_cols[0]
            for col in numeric_cols:
                if any(x in col.lower() for x in ['revenue', 'sales', 'price', 'amount', 'total', 'profit']):
                    metric_col = col
                    break
            avg_val = df[metric_col].mean()
            val_str = f"{avg_val:,.2f}" if avg_val > 1 else f"{avg_val:.4f}"
            kpis.append({"label": f"Avg {metric_col}", "value": val_str})

        # 3. Chart Generation
        charts = []
        
        # Datetime -> Line Chart
        if datetime_cols and numeric_cols:
            dt_col = datetime_cols[0]
            num_col = numeric_cols[0]
            for col in numeric_cols:
                if any(x in col.lower() for x in ['revenue', 'sales', 'price', 'amount']):
                    num_col = col
                    break
            charts.append({
                "type": "line",
                "title": f"Trend: {num_col} over Time",
                "x": dt_col,
                "y": num_col
            })
            
        # Categorical -> Bar Chart
        if categorical_cols:
            cat_col = categorical_cols[0]
            charts.append({
                "type": "bar",
                "title": f"Distribution: Top {cat_col}",
                "x": cat_col,
                "y": "count" # UI should know to aggregate count
            })
            
        # Numeric -> Histogram
        if numeric_cols:
            num_col = numeric_cols[0]
            for col in numeric_cols:
                if any(x in col.lower() for x in ['age', 'score', 'rating', 'value']):
                    num_col = col
                    break
            charts.append({
                "type": "histogram",
                "title": f"Frequency: {num_col}",
                "x": num_col
            })
            
        # Numeric Correlations -> Scatter Plot
        if len(numeric_cols) >= 2:
            c1, c2 = numeric_cols[0], numeric_cols[1]
            try:
                corr = df[numeric_cols].corr().abs()
                np.fill_diagonal(corr.values, 0)
                if not corr.isna().all().all():
                    c1, c2 = corr.unstack().idxmax()
            except:
                pass
            charts.append({
                "type": "scatter",
                "title": f"Correlation: {c1} vs {c2}",
                "x": c1,
                "y": c2
            })
            
        dashboard_config = {
            "kpis": kpis,
            "charts": charts
        }
        
        # 4. Save to Database
        db.query(DatasetDashboard).filter(DatasetDashboard.dataset_id == dataset_id).delete()
        dash = DatasetDashboard(dataset_id=dataset_id, dashboard_config=dashboard_config)
        db.add(dash)
        db.commit()
        
        logger.info(f"Dashboard config built for dataset {dataset_id}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Dashboard generation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
