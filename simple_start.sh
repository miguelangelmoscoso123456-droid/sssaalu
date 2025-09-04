#!/bin/bash
set -e
echo "Starting Simple Essalud API..."
export PORT=${PORT:-8000}
echo "PORT: $PORT"
echo "Starting uvicorn on port $PORT"
python simple_main.py
