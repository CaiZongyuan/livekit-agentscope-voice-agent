# LiveKit AgentScope Voice Agent

**English | [中文](./README-zh.md)**

A real-time voice AI agent powered by LiveKit, integrating multiple speech recognition and text-to-speech providers with AgentScope framework support.

## 🎯 Features

- **Real-time Voice Processing**: Low-latency speech-to-text and text-to-speech
- **Multiple TTS Providers**:
  - **Cloud-based**: ElevenLabs, Minimax, QwenTTS
  - **Local**: KokoroTTS, IndexTTS 1.5 (requires specific downloaded versions)
- **Speech Recognition**: Qwen ASR for Chinese speech recognition
- **Performance Monitoring**: Comprehensive metrics collection and real-time monitoring
- **Bilingual Support**: Chinese and English language capabilities
- **WebRTC Integration**: Built on LiveKit for scalable real-time communication
- **Modern Web Interface**: React-based frontend with Next.js

## 🏗️ Architecture

### Backend (Python)
- **Voice Agent Core**: LiveKit-based agent implementation
- **Custom Providers**: Extensible speech recognition and synthesis providers
- **Metrics Collection**: Real-time performance monitoring and analytics
- **AgentScope Integration**: Seamless integration with AgentScope framework

### Frontend (React)
- **Next.js Application**: Modern web interface for voice interactions
- **LiveKit Client SDK**: Real-time audio communication
- **Responsive Design**: Built with Tailwind CSS and modern React patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm (for frontend dependencies)
- uv (Python package manager)
- LiveKit CLI

### Backend Setup

1. **Clone and setup**:
```bash
git clone <repository-url>
cd livekit-agentscope-voice-agent

# Install dependencies using uv
uv sync

# Install LiveKit CLI
# Follow official installation guide: https://docs.livekit.io/home/cli/
# Or install via pip (alternative method):
pip install livekit-cli

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and configuration
```

2. **Configure LiveKit environment**:
```bash
# Get your LiveKit Server API keys by registering for free at:
# https://cloud.livekit.io/ (for cloud) or self-host your own server

# Edit .env file with your LiveKit configuration:
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.url
```

3. **Run the voice agent**:
```bash
# Basic version
uv run agent_server_demo.py start

# Version with metrics monitoring
uv run agent_server_with_metrics.py start
```

### Frontend Setup

> **Note**: The frontend is based on [livekit-examples/agent-starter-react](https://github.com/livekit-examples/agent-starter-react)

1. **Navigate to frontend directory**:
```bash
cd agent-starter-react
```

2. **(Optional) Update to latest version**:
```bash
# If you want to pull the latest updates from LiveKit examples:
git remote add upstream https://github.com/livekit-examples/agent-starter-react.git
git fetch upstream
git merge upstream/main
```

3. **Install dependencies**:
```bash
pnpm install
```

4. **Run development server**:
```bash
pnpm dev
```

5. **Open your browser** and navigate to `http://localhost:3000`

## ⚙️ Configuration

### Environment Variables

Required environment variables in `.env`:

```env
# Language Model
DEEPSEEK_API_KEY=your_deepseek_api_key

# Speech Services
ELEVEN_API_KEY=your_elevenlabs_api_key
MINIMAX_API_KEY=your_minimax_api_key
DASHSCOPE_API_KEY=your_qwen_asr_api_key

# LiveKit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.url
```

### Speech Providers Configuration

#### Qwen ASR (Chinese Speech Recognition)
- Model: `qwen3-asr-flash`
- Language: `zh` (Chinese)
- Features: Inverse text normalization, streaming support

#### TTS Providers

##### Cloud-based TTS
1. **ElevenLabs TTS**: High-quality voice synthesis with multiple voice options
   - API Key: `ELEVEN_API_KEY`
   - Natural-sounding voices with emotional range

2. **Minimax TTS**: Cloud-based Chinese and English synthesis
   - API Key: `MINIMAX_API_KEY`
   - Models: `speech-2.6-hd`, various voice options
   - Strong Chinese language support

3. **Qwen TTS**: Alibaba's text-to-speech service
   - API Key: `DASHSCOPE_API_KEY` (same as ASR)
   - Optimized for Chinese language

##### Local TTS

1. **Kokoro TTS**: Local synthesis engine
   - **Download**: [Kokoro TTS Package](https://pan.quark.cn/s/77eb46560914)
   - **Reference**: [Setup Tutorial](https://www.bilibili.com/video/BV1ziuBzyEjF/)
   - **API Format**: `http://localhost:9880/?text={text}&speaker={audio_path}&speed=1.0`
   - **Default Speakers**:
     - `speaker_en=am_adam_男.pt`
     - `speaker_zh=zm_029.pt`
   - No internet connection required
   - Fast inference speed

2. **Index-TTS-v1.5**: Concurrent local TTS with enhanced features
   - **Download**: [Index-TTS-v1.5 Package](https://pan.quark.cn/s/d3d521cccf91)
   - **Batch Tasks**: [Batch Task Files](https://pan.quark.cn/s/eb3d65587e6b)
   - **Reference**: [Setup Tutorial](https://www.bilibili.com/video/BV1RkT2zREHs)
   - **API Format**: `http://localhost:9880/?text={text}&speaker={voice_model}&volume=1.9`
   - **Features**:
     - Concurrent processing (solves multi-device request crashes)
     - Volume control
     - Batch task support
     - API interface support
     - RTX 50 series GPU support
     - Works with 4GB VRAM
   - High-quality voice synthesis
   - Custom voice model support

3. **FishSpeech 1.5.1**: Alternative local TTS option
   - **Download**: [FishSpeech Package](https://pan.quark.cn/s/bc0db941ebda)
   - **Reference**: [Setup Tutorial](https://www.bilibili.com/video/BV1YrYjzNEHf)
   - **API Format**: `http://localhost:9880?text={text}&speaker={voice_description}`
   - **Note**: Requires custom provider implementation based on the video tutorial
   - High-quality female voice support
   - Setup instructions in `providers/` directory

## 📊 Monitoring and Metrics

The agent includes comprehensive performance monitoring:

- **LLM Metrics**: Token usage, processing speed, time-to-first-token
- **STT Metrics**: Recognition latency, real-time factor, streaming performance
- **TTS Metrics**: First-byte latency, synthesis time, audio duration
- **EOU Metrics**: End-of-utterance detection performance

Metrics are sent to a WebSocket monitoring server and logged to console for debugging.

## 🛠️ Development

### Project Structure

```
livekit-agentscope-voice-agent/
├── agent_server_demo.py              # Basic voice agent implementation
├── agent_server_with_metrics.py      # Agent with performance monitoring
├── providers/                        # Custom speech provider implementations
│   ├── qwen_asr_stt.py              # Qwen speech-to-text provider
│   ├── kokoro_tts.py                # Kokoro text-to-speech provider
│   ├── local_indexTTS.py            # Local Index TTS provider
│   └── local_indextts_chaos.py      # Alternative local TTS provider
├── agent-starter-react/             # React frontend (based on livekit-examples)
│   └── # Originally from: https://github.com/livekit-examples/agent-starter-react
└── pyproject.toml                   # Python project configuration
```

### Adding Custom Providers

1. **Create a new provider** in the `providers/` directory
2. **Extend the appropriate LiveKit base class**:
   - `stt.STT` for speech recognition
   - `tts.TTS` for text-to-speech
3. **Implement required methods** and handle authentication
4. **Add metrics collection** if performance monitoring is needed
5. **Update the agent configuration** to use your new provider

### Running Tests

```bash
# Python tests (if implemented)
pytest

# Frontend tests
cd agent-starter-react
pnpm test
```

### Building for Production

```bash
# Backend
uv sync --production

# Frontend
cd agent-starter-react
pnpm build
pnpm start
```

### Frontend Maintenance

Since the frontend is based on LiveKit examples, you may want to keep it updated:

```bash
cd agent-starter-react

# Check for updates periodically
git remote -v  # Verify upstream remote exists
git fetch upstream
git log --oneline HEAD..upstream/main  # See what's new

# Merge updates (when needed)
git merge upstream/main

# Resolve any conflicts and test
pnpm install
pnpm dev
```

## 🌐 Deployment

### Backend Deployment

1. **Deploy to cloud server** or containerize with Docker
2. **Configure environment variables** for production
3. **Set up LiveKit server** (cloud or self-hosted)
4. **Configure monitoring server** for metrics collection

### Frontend Deployment

```bash
cd agent-starter-react
pnpm build
# Deploy the .next directory to your hosting platform
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [LiveKit](https://livekit.io/) - Open source WebRTC infrastructure
- [AgentScope](https://github.com/modelscope/AgentScope) - Multi-agent communication framework
- [Qwen ASR](https://github.com/QwenLM/Qwen) - Alibaba's speech recognition model
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - High-quality text-to-speech synthesis
