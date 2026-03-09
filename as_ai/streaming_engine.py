import os
import time
import json
import logging
import threading
import datetime
import pandas as pd
from kafka import KafkaConsumer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.ensemble import IsolationForest
from as_ai.insights import generate_dataset_insights

# Directories
CHARTS_STREAMING_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "streaming")
os.makedirs(CHARTS_STREAMING_DIR, exist_ok=True)

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)
STREAM_INSIGHTS_FILE = os.path.join(MEMORY_DIR, "stream_insights.json")

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Logger for stream alerts
stream_logger = logging.getLogger("stream_alerts")
stream_logger.setLevel(logging.WARNING)
fh = logging.FileHandler(os.path.join(LOGS_DIR, "stream_alerts.log"))
fh.setFormatter(logging.Formatter('%(asctime)s | [ALERT] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
stream_logger.addHandler(fh)

STREAM_STATUS = {
    "records_processed": 0,
    "anomalies_detected": 0,
    "last_update": None,
    "is_running": False
}

def plot_stream_anomaly(df: pd.DataFrame, column: str, anomalies: pd.Series):
    """
    Plots the anomaly and saves the chart.
    """
    plt.figure(figsize=(8, 4))
    sns.scatterplot(x=df.index, y=df[column], hue=anomalies.map({1: 'Normal', -1: 'Anomaly'}), palette={'Normal': 'blue', 'Anomaly': 'red'})
    plt.title(f'Real-Time Anomaly Detection: {column}')
    plt.tight_layout()
    timestamp = int(time.time())
    filename = f"stream_anomaly_{column}_{timestamp}.png"
    filepath = os.path.join(CHARTS_STREAMING_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    return f"/charts/streaming/{filename}"

def detect_stream_anomalies(df: pd.DataFrame):
    """
    Runs IsolationForest on recent data batch to detect point anomalies.
    """
    numeric_cols = df.select_dtypes(include='number').columns
    if len(df) < 10 or len(numeric_cols) == 0:
        return
        
    for col in numeric_cols:
        model = IsolationForest(contamination=0.05, random_state=42)
        X = df[[col]].fillna(df[col].median())
        preds = model.fit_predict(X)
        
        # If the newest record is an anomaly (-1)
        if preds[-1] == -1:
            STREAM_STATUS["anomalies_detected"] += 1
            stream_logger.warning(f"unusual spike detected in {col} (Value: {df.iloc[-1][col]})")
            plot_stream_anomaly(df.tail(50), col, pd.Series(preds[-50:], index=df.tail(50).index))

def _consume_loop(topic_name: str, active_dataset_list: list, dataset_index: int):
    """
    Internal loop that runs in a separate thread.
    """
    STREAM_STATUS["is_running"] = True
    
    try:
        # Kafka configuration matching standard local docker-compose
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        records_since_insight = 0
        
        for message in consumer:
            if not STREAM_STATUS["is_running"]:
                break
                
            data = message.value
            new_row = pd.DataFrame([data])
            
            # Append to active dataset directly
            df = active_dataset_list[dataset_index]
            df = pd.concat([df, new_row], ignore_index=True)
            active_dataset_list[dataset_index] = df
            
            STREAM_STATUS["records_processed"] += 1
            STREAM_STATUS["last_update"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            records_since_insight += 1
            
            # Anomaly checks on stream ingest
            detect_stream_anomalies(df)
            
            # Rehydrate insights periodically
            if records_since_insight >= 100:
                insights = generate_dataset_insights(df)
                with open(STREAM_INSIGHTS_FILE, "w") as f:
                    json.dump(insights, f, indent=4)
                records_since_insight = 0
                
    except Exception as e:
        stream_logger.error(f"Kafka Consumer Error: {str(e)}")
        STREAM_STATUS["is_running"] = False

def start_stream_consumer(topic_name: str, active_dataset_list: list, dataset_index: int = 0):
    """
    Starts the Kafka consumer background pipeline. 
    """
    if STREAM_STATUS["is_running"]:
        return {"status": "streaming already running"}
        
    if len(active_dataset_list) <= dataset_index:
        active_dataset_list.append(pd.DataFrame())
        
    thread = threading.Thread(
        target=_consume_loop, 
        args=(topic_name, active_dataset_list, dataset_index),
        daemon=True
    )
    thread.start()
    
    return {"status": "streaming started"}

def get_stream_status():
    return STREAM_STATUS
