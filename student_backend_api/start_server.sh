#!/bin/bash
#
# Start the FastAPI server on port 3001 (default).
# Can override host/port as needed.
#
# Usage: bash start_server.sh [host] [port]
set -e
HOST="${1:-0.0.0.0}"
PORT="${2:-3001}"

echo "Starting FastAPI backend on $HOST:$PORT ..."
uvicorn src.api.main:app --host "$HOST" --port "$PORT" --reload
