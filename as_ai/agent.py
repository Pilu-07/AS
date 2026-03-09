import warnings
from pandasai import Agent
from as_ai.config import get_llm

def create_agent(dataframes) -> Agent:
    """Initializes and returns a PandasAI Agent wrapped around the provided dataframe(s)."""
    llm = get_llm()
    
    import os
    CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts")
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
    # Suppress deprecation warnings about the 'config' parameter if expected
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        agent = Agent(dataframes, config={"llm": llm, "save_charts": True, "save_charts_path": CHARTS_DIR})
        
    return agent
