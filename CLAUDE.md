# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LiveKit voice agent project that integrates with AgentScope and provides real-time speech-to-text, language processing, and text-to-speech capabilities. The project consists of:

- **Python Voice Agent Backend**: LiveKit agents with custom STT/TTS providers and metrics collection
- **React Frontend**: Next.js web interface for voice interactions (`agent-starter-react/`)

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

### Technology Stack

- **Backend**: Python 3.12+, LiveKit Agents, OpenAI/DeepSeek LLM
- **Frontend**: Next.js 15.5.2, React 19, LiveKit client SDK
- **Speech**: Qwen ASR, Silero VAD, custom TTS implementations
- **Package Management**: pip with pyproject.toml (Python), pnpm (Node.js)

### Key Integrations

- **LiveKit**: Real-time WebRTC communication
- **OpenAI/DeepSeek**: Language model integration
- **Qwen ASR**: Chinese speech recognition
- **Minimax TTS**: Cloud text-to-speech
- **Local TTS**: On-premise speech synthesis

## Environment Configuration

Required environment variables (configure in `.env`):
- `DASHSCOPE_API_KEY`: Alibaba Qwen ASR API key
- LiveKit server credentials (if using cloud LiveKit)
- TTS service endpoints (for local TTS providers)

## Development Notes

### Running the Voice Agent

1. Ensure virtual environment is activated and dependencies installed
2. Configure `.env` with required API keys
3. Start the agent using either `agent_server_demo.py` (basic) or `agent_server_with_metrics.py` (with monitoring)
4. Use the React frontend to connect and interact with the voice agent

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
- All metrics are forwarded to WebSocket monitoring server and logged to console