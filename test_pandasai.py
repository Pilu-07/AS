import pandas as pd
from pandasai import Agent
from pandasai.llm.fake import FakeLLM
import os
import sys

csv_path = "examples/data/loans_payments.csv"

if not os.path.exists(csv_path):
    print(f"Error: Could not find dataset at {csv_path}", file=sys.stderr)
    sys.exit(1)

print(f"Loading data from {csv_path}")
try:
    df = pd.read_csv(csv_path)
    print(f"Data loaded successfully. Shape: {df.shape}")
    
    # Use FakeLLM to return a static mock response
    # This proves the environment and PandasAI agent flow works locally without incurring OpenAI costs or requiring an API key.
    mock_code = """
try:
    execute_sql_query('SELECT 1')
except Exception:
    pass
result = {"type": "number", "value": 10565.4}
"""
    llm = FakeLLM(output=mock_code)
    
    agent = Agent(df, config={"llm": llm})
    print("Agent created successfully.")
    
    question = "What is the average loan amount?"
    print(f"Asking question: '{question}'")
    result = agent.chat(question)
    
    print("Result:", result)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error occurred: {e}", file=sys.stderr)
    sys.exit(1)
