#!/bin/bash

echo "🚀 Starting AI Resume Analyzer..."
echo ""

# Start backend in background
echo "Starting backend server on port 8000..."
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start web server in background
echo "Starting web interface on port 8081..."
python3 -m http.server 8081 --directory web_interface &
WEB_PID=$!

# Wait a bit for web server to start
sleep 2

# Open browser
echo "Opening browser..."
open http://localhost:8081

echo ""
echo "✅ Application is running!"
echo "   Backend: http://127.0.0.1:8000"
echo "   Web Interface: http://localhost:8081"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $WEB_PID; echo 'Servers stopped'; exit" INT
wait
