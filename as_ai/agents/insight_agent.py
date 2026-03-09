import pandas as pd
from typing import Dict, Any

from as_ai.ai_insights import generate_ai_insights, detect_anomalies

class InsightAgent:
    """
    Derives business intelligence, anomaly tracking, and LLM text insights
    from the structured metadata.
    """
    
    def generate_insights(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        anomalies = detect_anomalies(dataframe)
        
        # Extract qualitative LLM insights
        ai_insights = generate_ai_insights(dataframe)
        
        return {
            "trends": ai_insights.get("key_trends"),
            "anomalies": {
                "detected": anomalies,
                "summary": ai_insights.get("anomalies")
            },
            "business_insights": ai_insights.get("business_insights"),
            "recommendations": ai_insights.get("recommended_visualizations", [])
        }
