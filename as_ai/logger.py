import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "query_history.log")

def log_query(query: str, result: str):
    """Appends to the query_history.log file with the timestamp, user query, and result summary."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)
        
    timestamp = datetime.now().isoformat()
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}]\n")
        f.write(f"Query: {query}\n")
        f.write(f"Result: {result}\n")
        f.write("-" * 50 + "\n")
