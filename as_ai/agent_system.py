import pandas as pd
from typing import Dict, Any

from as_ai.agents.planner_agent import PlannerAgent
from as_ai.agents.data_agent import DataAgent
from as_ai.agents.ml_agent import MLAgent
from as_ai.agents.insight_agent import InsightAgent
from as_ai.agents.viz_agent import VisualizationAgent

class AgentManager:
    """
    Central Coordinator. Initializes and coordinates the execution flow 
    of specialized AI agents sequentially operating across a dataset.
    """
    
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset
        self.planner = PlannerAgent()
        self.data_agent = DataAgent()
        self.ml_agent = MLAgent()
        self.insight_agent = InsightAgent()
        self.viz_agent = VisualizationAgent()

    def run_full_analysis(self) -> Dict[str, Any]:
        """
        Executes the multi-agent pipeline:
        1. Plans the logic.
        2. Cleans the data.
        3. Tests ML bounds.
        4. Extracts strategic insights.
        5. Visualizes structures.
        """
        # 1. Planner Agent
        plan = self.planner.create_plan(self.dataset)
        
        # 2. Data Cleaning Agent
        cleaned_data = self.data_agent.clean_data(self.dataset)
        
        # 3. ML Agent
        model_results = self.ml_agent.train_models(cleaned_data)
        
        # 4. Insight Agent
        insights = self.insight_agent.generate_insights(cleaned_data)
        
        # 5. Visualization Agent
        charts = self.viz_agent.generate_visualizations(cleaned_data)
        
        return {
            "plan": plan,
            "models": model_results,
            "insights": insights,
            "charts": charts
        }
