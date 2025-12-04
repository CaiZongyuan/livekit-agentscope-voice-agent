#!/bin/bash

echo "🛑 Stopping LiveKit AgentScope Voice Agent Services..."

# Load PIDs from file if it exists
if [ -f .service_pids ]; then
    source .service_pids

    if [ ! -z "$LIVEKIT_PID" ]; then
        echo "🛑 Stopping LiveKit server (PID: $LIVEKIT_PID)..."
        kill $LIVEKIT_PID 2>/dev/null
        echo "✅ LiveKit server stopped"
    fi

    if [ ! -z "$TOKEN_SERVER_PID" ]; then
        echo "🛑 Stopping Token server (PID: $TOKEN_SERVER_PID)..."
        kill $TOKEN_SERVER_PID 2>/dev/null
        echo "✅ Token server stopped"
    fi

    if [ ! -z "$VOICE_AGENT_PID" ]; then
        echo "🛑 Stopping Voice Agent (PID: $VOICE_AGENT_PID)..."
        kill $VOICE_AGENT_PID 2>/dev/null
        echo "✅ Voice Agent stopped"
    fi

    rm -f .service_pids
else
    # If no PID file, kill by port
    echo "⚠️  No PID file found, stopping services by port..."

    # Kill processes on ports 7880, 8008
    for port in 7880 8008; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "🛑 Stopping process on port $port (PID: $pid)..."
            kill $pid
        fi
    done

    # Kill agent_server_demo.py processes
    pkill -f "agent_server_demo.py" 2>/dev/null
fi

# Wait a moment for processes to stop
sleep 2

echo "✅ All services have been stopped!"