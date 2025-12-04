#!/bin/bash

echo "🚀 Starting LiveKit AgentScope Voice Agent Services..."

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready on port $port..."

    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            echo "✅ $service_name is ready!"
            return 0
        fi

        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done

    echo "❌ $service_name failed to start within timeout period"
    return 1
}

# Start LiveKit server
echo "1️⃣ Starting LiveKit server..."
if ! check_port 7880; then
    livekit-server --dev --bind 0.0.0.0 --port 7880 &
    LIVEKIT_PID=$!

    if wait_for_service 7880 "LiveKit server"; then
        echo "✅ LiveKit server started successfully (PID: $LIVEKIT_PID)"
    else
        echo "❌ Failed to start LiveKit server"
        exit 1
    fi
else
    echo "⚠️  LiveKit server is already running on port 7880"
fi

# Start token server
echo "2️⃣ Starting token server..."
if ! check_port 8008; then
    uv run python server.py &
    TOKEN_SERVER_PID=$!

    if wait_for_service 8008 "Token server"; then
        echo "✅ Token server started successfully (PID: $TOKEN_SERVER_PID)"
    else
        echo "❌ Failed to start token server"
        kill $LIVEKIT_PID 2>/dev/null
        exit 1
    fi
else
    echo "⚠️  Token server is already running on port 8008"
fi

# Start voice agent
echo "3️⃣ Starting voice agent..."
cd .. && uv run python agent_server_demo.py start&
VOICE_AGENT_PID=$!

# Give the voice agent a moment to initialize
sleep 3

if kill -0 $VOICE_AGENT_PID 2>/dev/null; then
    echo "✅ Voice agent started successfully (PID: $VOICE_AGENT_PID)"
else
    echo "❌ Failed to start voice agent"
    kill $LIVEKIT_PID 2>/dev/null
    kill $TOKEN_SERVER_PID 2>/dev/null
    exit 1
fi

# Save PIDs to file for cleanup
echo "LIVEKIT_PID=$LIVEKIT_PID" > .service_pids
echo "TOKEN_SERVER_PID=$TOKEN_SERVER_PID" >> .service_pids
echo "VOICE_AGENT_PID=$VOICE_AGENT_PID" >> .service_pids

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📋 Service Status:"
echo "   • LiveKit Server:  http://localhost:7880 (PID: $LIVEKIT_PID)"
echo "   • Token Server:    http://localhost:8008 (PID: $TOKEN_SERVER_PID)"
echo "   • Voice Agent:     Running (PID: $VOICE_AGENT_PID)"
echo ""
echo "🌐 You can now connect your clients:"
echo "   • Web Client:      cd ../agent-starter-react && pnpm dev"
echo "   • Mobile Client:   cd ../react-native && bun expo run:ios"
echo ""
echo "🛑 To stop all services, run: ./stop_services.sh"
echo "   Or press Ctrl+C to stop all services"

# Handle script termination
trap 'echo ""; echo "🛑 Stopping all services..."; kill $LIVEKIT_PID $TOKEN_SERVER_PID $VOICE_AGENT_PID 2>/dev/null; rm -f .service_pids; echo "✅ All services stopped"; exit 0' INT TERM

# Wait for all background processes
wait