# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiveKit voice agent project that integrates with AgentScope and provides real-time speech-to-text, language processing, and text-to-speech capabilities. The project consists of:

- **Python Voice Agent Backend**: LiveKit agents with custom STT/TTS providers and metrics collection
- **React Frontend**: Next.js web interface for voice interactions (`agent-starter-react/`)
- **React Native Mobile Client**: iOS and Android mobile application (`react-native/`)
- **Token Server**: Authentication and room management server (`server/`)

## Development Commands

### Python Voice Agent

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Install dependencies (if needed)
uv sync

# Run the demo voice agent
python agent_server_demo.py

# Run the voice agent with metrics collection
python agent_server_with_metrics.py

# Environment setup - copy .env.example to .env and configure:
# - DASHSCOPE_API_KEY (for Qwen ASR)
# - LiveKit server configuration
# - DEEPSEEK_API_KEY (for LLM integration)

# Start token server (required for mobile clients)
uv run server/server.py
```

### React Frontend

```bash
cd agent-starter-react

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Lint code
pnpm lint

# Format code
pnpm format
```

### React Native Mobile Client

```bash
cd react-native

# Install dependencies
bun install

# Build and run on iOS simulator
bun expo run:ios

# Build and run on iOS device
bun expo run:ios --device

# Build and run on Android
bunx expo run:android

# Environment setup - copy .env.example to .env and configure:
# - EXPO_PUBLIC_TOKEN_SERVER_URL: URL to token server endpoint
# - For local development with simulators/devices:
#   - iOS Simulator: http://127.0.0.1:8008/token
#   - Android Simulator: http://10.0.2.2:8008/token
#   - Real Device: http://<your-LAN-IP>:8008/token

# Note: Expo Go cannot be used - must build the project first
```

### Token Server

```bash
cd server

# Install dependencies (if needed)
uv sync

# Run the token server
uv run server.py

# Default configuration:
# - Port: 8008
# - LiveKit API URL: ws://localhost:7880 (configurable via .env)
# - API Key: devkey, Secret: secret (configurable via .env)
```

## Architecture

### Voice Agent Components

1. **Core Agent Classes** (`agent_server_demo.py`, `agent_server_with_metrics.py`):
   - `Assistant`: Basic voice agent implementation
   - `MetricsAssistant`: Enhanced agent with performance monitoring

2. **Custom Providers** (`providers/`):
   - **Qwen ASR Provider** (`qwen_asr_stt.py`): Alibaba Qwen speech-to-text integration
   - **Kokoro TTS** (`kokoro_tts.py`): Local text-to-speech synthesis
   - **Local Index TTS** (`local_indexTTS.py`): Index-based TTS service
   - **Local Chaos TTS** (`local_indextts_chaos.py`): Alternative TTS implementation

3. **Metrics Collection** (`agent_server_with_metrics.py`):
   - Real-time performance monitoring via WebSocket
   - LLM, STT, TTS, and EOU (End of Utterance) metrics
   - Metrics sent to monitoring server at `ws://localhost:8001/ws`

4. **Token Server** (`server/server.py`):
   - FastAPI-based authentication server
   - Generates LiveKit tokens for client connections
   - Handles room creation and participant management
   - Supports mobile clients with proper CORS configuration

### Technology Stack

- **Backend**: Python 3.12+, LiveKit Agents, OpenAI/DeepSeek LLM, FastAPI
- **Web Frontend**: Next.js 15.5.2, React 19, LiveKit client SDK
- **Mobile Frontend**: React Native with Expo, LiveKit client SDK
- **Speech**: Qwen ASR, Silero VAD, custom TTS implementations
- **Package Management**: pip with pyproject.toml (Python), pnpm (Node.js), bun (React Native)

### Key Integrations

- **LiveKit**: Real-time WebRTC communication
- **Expo**: React Native development platform and build service
- **FastAPI**: Token server framework for authentication
- **OpenAI/DeepSeek**: Language model integration
- **Qwen ASR**: Chinese speech recognition
- **Minimax TTS**: Cloud text-to-speech
- **Local TTS**: On-premise speech synthesis

## Environment Configuration

Required environment variables (configure in `.env`):
- `DASHSCOPE_API_KEY`: Alibaba Qwen ASR API key
- `DEEPSEEK_API_KEY`: DeepSeek LLM API key
- `LIVEKIT_API_KEY`: LiveKit server API key
- `LIVEKIT_API_SECRET`: LiveKit server API secret
- `LIVEKIT_URL`: LiveKit server WebSocket URL
- TTS service endpoints (for local TTS providers)

### React Native Environment Variables

Configure in `react-native/.env`:
- `EXPO_PUBLIC_TOKEN_SERVER_URL`: Token server endpoint URL
- `EXPO_PUBLIC_LIVEKIT_URL`: LiveKit server URL (optional)
- `EXPO_PUBLIC_PARTICIPANT_TOKEN`: Pre-configured token (optional)

### Token Server Environment Variables

Configure in root `.env` (shared with voice agent):
- `PORT`: Token server port (default: 8008)
- `LIVEKIT_API_KEY`: LiveKit server API key
- `LIVEKIT_API_SECRET`: LiveKit server API secret
- `LIVEKIT_URL`: LiveKit server WebSocket URL

## Development Notes

### Running the Complete System

For a complete development setup:

1. **Start LiveKit Server**:
   ```bash
   livekit-server --dev --bind 0.0.0.0 --port 7880
   ```

2. **Start Token Server** (required for mobile clients):
   ```bash
   uv run server/server.py
   ```

3. **Start Voice Agent**:
   ```bash
   uv run agent_server_demo.py start  # or agent_server_with_metrics.py
   ```

4. **Connect with Clients**:
   - **Web**: Navigate to `agent-starter-react` and run `pnpm dev`
   - **Mobile**: Navigate to `react-native` and run `bun expo run:ios` or `bunx expo run:android`

### Mobile Client Development

When working with React Native:

1. **Environment Setup**: Different IP configurations for different targets:
   - iOS Simulator: `http://127.0.0.1:8008/token`
   - Android Simulator: `http://10.0.2.2:8008/token`
   - Real Device: `http://<your-LAN-IP>:8008/token`

2. **Build Requirements**: Must build the project first - Expo Go cannot be used
3. **Token Integration**: Mobile clients use the token server for authentication and room management

### Network Configuration for Mobile Development

For mobile client connectivity:
- LiveKit server must bind to `0.0.0.0` for LAN access
- Token server must be accessible from mobile devices
- Proper CORS configuration in token server for mobile requests
- Firewall rules may need to be configured for local development

### Custom Provider Development

When adding new speech providers:
1. Extend appropriate LiveKit base classes (`stt.STT` or `tts.TTS`)
2. Implement required abstract methods
3. Handle authentication and API integration
4. Add metrics collection hooks if needed
5. Test with both demo and metrics-enabled agents

### Metrics and Monitoring

The metrics-enabled agent provides real-time performance data:
- Token usage and processing speed (LLM)
- Speech recognition latency and accuracy (STT)
- Audio generation timing (TTS)
- End-of-utterance detection performance
- All metrics are forwarded to WebSocket monitoring server at `ws://localhost:8001/ws` and logged to console

### Project Structure for Development

```
livekit-agentscope-voice-agent/
├── react-native/                     # Mobile client directory
│   ├── README.md                     # English setup guide
│   ├── README-zh.md                  # Chinese setup guide
│   ├── .env.example                  # Environment variables template
│   └── ...                          # React Native project files
├── server/                          # Token server directory
│   ├── server.py                    # FastAPI token server
│   └── ...                          # Server configuration files
├── providers/                        # Custom speech providers
├── agent_server_*.py                 # Voice agent implementations
└── agent-starter-react/              # Web frontend (clone separately)
```

### Testing Different Client Types

- **Web Client**: Direct LiveKit connection with hardcoded tokens or sandbox mode
- **Mobile Client**: Token server integration with automatic room creation
- **Mixed Environment**: Both clients can connect to the same LiveKit server and agent simultaneously