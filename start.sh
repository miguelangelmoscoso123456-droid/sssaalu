#!/bin/bash
set -e
echo "Starting Essalud API..."
echo "PORT: ${PORT:-8000}"
export PORT=${PORT:-8000}
echo "Starting uvicorn on port $PORT"
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
