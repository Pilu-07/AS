import os
import json
import datetime
from typing import List, Dict, Any

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(MEMORY_DIR, "analysis_history.json")
FEEDBACK_FILE = os.path.join(MEMORY_DIR, "feedback.json")

def load_analysis_history() -> List[Dict[str, Any]]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def load_feedback() -> Dict[str, int]:
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_analysis_result(data: Dict[str, Any]):
    history = load_analysis_history()
    
    # Enrich with timestamp and a unique ID
    record = {
        **data,
        "analysis_id": f"analysis_{len(history) + 1}_{int(datetime.datetime.now().timestamp())}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    history.append(record)
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)
        
    return record["analysis_id"]

def save_feedback(analysis_id: str, rating: int):
    feedback = load_feedback()
    feedback[analysis_id] = rating
    
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=4)
        
    return True

def recommend_model(dataset_schema: List[str], target_column: str = None) -> str:
    """
    Recommends the best model architecture by searching previous high-performing 
    runs on similar schemas, factoring in human feedback ratings linearly.
    """
    history = load_analysis_history()
    if not history:
        return None
        
    feedback = load_feedback()
    
    schema_set = set(dataset_schema)
    best_score = -1
    recommended_model = None
    
    for record in history:
        # Check similarity (e.g. at least 30% feature overlap or identical target)
        record_features = set(record.get("features", []))
        overlap = len(schema_set.intersection(record_features))
        
        is_similar = overlap > 0 and (len(record_features) > 0 and overlap / len(record_features) > 0.3)
        if target_column and target_column == record.get("target_column"):
            is_similar = True
            
        if is_similar:
            # Base score from f1 or r2 approximations loosely bound 0-1
            base_metric = record.get("f1_score", 0.0)
            if not base_metric:
                base_metric = record.get("r2_score", 0.5) # rough fallback
                
            # Add feedback weight (Rating 1-5 scales mapped dynamically)
            rating = feedback.get(record.get("analysis_id", ""), 3) # default neutral 3
            
            # Simple heuristic: Score = metric + scaled rating bonus
            score = float(base_metric) + (rating * 0.1)
            
            if score > best_score:
                best_score = score
                recommended_model = record.get("best_model")
                
    return recommended_model
