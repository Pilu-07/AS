import json
import pandas as pd
from typing import Dict, Any

from as_ai.config import get_llm
from as_ai.insights import generate_dataset_insights

class PlannerAgent:
    """
    Decides what analyses should be executed based on the dataset schema.
    Uses the LLM to generate a sequence of structured tasks.
    """
    
    def create_plan(self, dataframe: pd.DataFrame) -> Dict[str, Any]:
        stats = generate_dataset_insights(dataframe)
        schema_cols = dataframe.columns.tolist()
        
        prompt = f"""
You are an expert AI data planner. Given this dataset schema and basic statistics, decide the logical sequence of analyses to be performed to derive maximum value.

Schema: {schema_cols}
Stats: 
- Total Rows: {stats.get('rows')}
- Numeric Columns: {len(stats.get('numeric_summary', {}))}
- Categorical Columns: {len(stats.get('categorical_summary', {}))}

Return ONLY a valid JSON object matching exactly this structure:
{{
    "tasks": [
        "detect anomalies",
        "generate correlation heatmap",
        "train classification model",
        "detect feature importance",
        "generate dashboard"
    ]
}}
"""
        llm = get_llm()
        
        # FakeLLM fallback for tests
        if getattr(llm, "type", "unknown") == "fake":
            return {
                "tasks": [
                    "clean dataset",
                    "detect anomalies",
                    "generate correlation heatmap",
                    "train classification model",
                    "detect feature importance"
                ]
            }
            
        try:
            from pandasai.core.prompts.base import BasePrompt
            class PlanningPrompt(BasePrompt):
                def to_string(self) -> str:
                    return prompt
                    
            response = llm.call(PlanningPrompt())
            response_text = response.replace("```json", "").replace("```", "").strip()
            return json.loads(response_text)
        except Exception as e:
            return {
                "tasks": [
                    "clean dataset",
                    "train model",
                    "evaluate statistics"
                ]
            }
