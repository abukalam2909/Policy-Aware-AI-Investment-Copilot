#!/usr/bin/env bash
# Start both FastAPI backend and React frontend
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "Starting FastAPI backend on http://localhost:8000 ..."
cd "$ROOT"
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting React frontend on http://localhost:5173 ..."
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
