import json
import pandas as pd
from typing import Dict, Any

from as_ai.config import get_llm
from as_ai.insights import generate_dataset_insights

def generate_data_story() -> Dict[str, Any]:
    """
    Simulates the AI Data Storytelling Engine to convert structured analysis outputs
    into natural-language stories, producing an Executive Summary.
    """
    
    prompt = """
You are an expert AI Data Storyteller. Convert the following dataset metrics into a business narrative.
Create a JSON object matching this exact structure containing an executive summary narrative, key drivers, and recommendations.

{
    "summary": "Customer churn increased 14% in Q3 due to X and Y...",
    "key_drivers": ["Low customer engagement", "High subscription price"],
    "recommendations": ["Introduce loyalty discounts", "Improve onboarding flow"]
}
"""
    
    llm = get_llm()
    
    if getattr(llm, "type", "unknown") == "fake":
        return {
            "summary": "The dataset analysis indicates a stable performance trajectory over the last quarter, though recent anomalies suggest potential supply chain disruptions.",
            "key_drivers": [
                "Consistent baseline revenue growth",
                "Spike in anomalous transactional events in the last week",
                "Model confidence remains high (F1: 0.94) for primary forecasting"
            ],
            "recommendations": [
                "Investigate isolation forest anomaly flags immediately",
                "Deploy retrained model to production",
                "Monitor real-time streams for further drift"
            ]
        }
    
    try:
        from pandasai.core.prompts.base import BasePrompt
        class StoryPrompt(BasePrompt):
            def to_string(self) -> str:
                return prompt
        
        response = llm.call(StoryPrompt())
        response_text = response.replace("```json", "").replace("```", "").strip()
        result_dict = json.loads(response_text)
        return result_dict
    except Exception as e:
        return {
            "summary": "Data storytelling generation failed. Falling back to default heuristics.",
            "key_drivers": ["System Error", str(e)],
            "recommendations": ["Verify LLM API configuration."]
        }
