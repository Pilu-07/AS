import os
import sys
import json

# Ensure the root directory is in the Python path to allow importing the as_ai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from as_ai.dataset_loader import load_dataset, get_schema
from as_ai.agent import create_agent
from as_ai.logger import log_query

def main():
    csv_paths = [
        "examples/data/loans_payments.csv",
        "examples/data/heart.csv"
    ]
    
    dataframes = []
    
    for path in csv_paths:
        print(f"Loading dataset from: {path}")
        try:
            df = load_dataset(path)
            dataframes.append(df)
            print(f"Data loaded successfully. Shape: {df.shape}")
            
            # Print Schema
            schema = get_schema(df)
            print("Schema:")
            print(json.dumps({
                "columns": schema["columns"],
                "dtypes": schema["dtypes"]
            }, indent=2))
        except Exception as e:
            print(f"Failed to load dataset {path}: {e}", file=sys.stderr)
            sys.exit(1)
        print("-" * 40)
        
    print("Initializing AS-AI Agent with multiple datasets...")
    try:
        agent = create_agent(dataframes) # Now passing a list of dataframes
        print("Agent created successfully.")
    except Exception as e:
        print(f"Failed to create agent: {e}", file=sys.stderr)
        sys.exit(1)
        
    question = "Which dataset has more rows?"
    print(f"\nUser Query: '{question}'")
    print("Processing...")
    
    try:
        result = agent.chat(question)
        print(f"\nResult: {result}")
        
        # Log query
        log_query(question, str(result))
        print("Query logged successfully.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nError occurred during query execution: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
