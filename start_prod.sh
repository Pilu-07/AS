#!/bin/bash
echo "Starting AS-AI Production Server..."
uvicorn as_ai.api.server:app --host 0.0.0.0 --port 8000 --workers 4
