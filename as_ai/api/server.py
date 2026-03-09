import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from as_ai.api.routes import router, limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AS-AI Data Analyst API",
    description="Backend AI engine powered by PandasAI",
    version="1.0.0"
)

import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(LOG_DIR, "server.log"), maxBytes=5000000, backupCount=5),
        logging.StreamHandler()
    ]
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://as-ai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)
app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")

CHARTS_STREAMING_DIR = os.path.join(CHARTS_DIR, "streaming")
os.makedirs(CHARTS_STREAMING_DIR, exist_ok=True)

CHARTS_AGENTS_DIR = os.path.join(CHARTS_DIR, "agents")
os.makedirs(CHARTS_AGENTS_DIR, exist_ok=True)

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# Include the routes from routes.py
app.include_router(router)

@app.get("/health")
def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("as_ai.api.server:app", host="127.0.0.1", port=8000, reload=True)
