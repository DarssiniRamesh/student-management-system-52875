#!/bin/bash
#
# Start the FastAPI server on port 3001 (default).
# Can override host/port as needed.
#
# Usage: bash start_server.sh [host] [port]
set -e
HOST="${1:-0.0.0.0}"
PORT="${2:-3001}"

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "No .env present. Copying from .env.example..."
    cp .env.example .env
  else
    echo "ERROR: .env file missing and no .env.example template found."
    exit 1
  fi
fi

echo "Starting FastAPI backend on $HOST:$PORT ..."
uvicorn src.api.main:app --host "$HOST" --port "$PORT" --reload
