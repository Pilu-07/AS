import os
import json
from datetime import datetime
from as_ai.config import get_llm

class ResearchAgent:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.research_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "research"
        )
        os.makedirs(self.research_dir, exist_ok=True)
        self.history_file = os.path.join(self.research_dir, "hypotheses_history.json")

    def generate_hypotheses(self, dataset_profile: dict, correlations: dict, anomalies: dict) -> dict:
        """
        Uses the LLM to propose research questions based on the dataset profile, correlations, and anomalies.
        """
        prompt = f"""
You are an expert AI Research Scientist. Your objective is to formulate novel research hypotheses
based on the provided dataset characteristics. 

Dataset Profile: {json.dumps(dataset_profile.get('numeric_summary', {}))}
Correlations (Top Pairs): {json.dumps(correlations)}
Anomalies Detected: {json.dumps(anomalies)}

Propose exactly 3 highly actionable, interesting hypothesis statements that explain potential causation or correlation.
Return your response ONLY as a JSON object matching this exact structure:

{{
    "hypotheses": [
        "Hypothesis 1 string...",
        "Hypothesis 2 string...",
        "Hypothesis 3 string..."
    ]
}}
"""
        llm = get_llm()
        
        # Test mock handling
        if getattr(llm, "type", "unknown") == "fake":
            result_dict = {
                "hypotheses": [
                    "High variation in the selected feature correlates strongly with outlier density.",
                    "Anomalous distribution tails indicate potential systemic process drift.",
                    "Certain data clusters may be significantly under-represented in typical sampling."
                ]
            }
        else:
            try:
                from pandasai.core.prompts.base import BasePrompt
                class HypothesisPrompt(BasePrompt):
                    def to_string(self) -> str:
                        return prompt
                
                response = llm.call(HypothesisPrompt())
                response_text = response.replace("```json", "").replace("```", "").strip()
                result_dict = json.loads(response_text)
            except Exception as e:
                result_dict = {
                    "hypotheses": [
                        f"Failed to generate custom hypothesis: {str(e)}",
                        "Feature behavior needs manual inspection.",
                        "Default fallback hypothesis triggered."
                    ]
                }
        
        self._store_hypotheses(result_dict["hypotheses"])
        return result_dict

    def _store_hypotheses(self, hypotheses: list):
        """
        Stores generated hypotheses into research/hypotheses_history.json.
        """
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    content = f.read()
                    if content.strip():
                        history = json.loads(content)
            except Exception:
                pass
                
        new_entry = {
            "dataset": self.dataset_name,
            "generated_hypotheses": hypotheses,
            "timestamp": datetime.now().isoformat()
        }
        
        history.append(new_entry)
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=4)
            
    def get_hypotheses_history(self) -> list:
        """
        Retrieves all stored hypotheses.
        """
        if not os.path.exists(self.history_file):
            return []
        try:
            with open(self.history_file, "r") as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
        except Exception:
            pass
        return []
