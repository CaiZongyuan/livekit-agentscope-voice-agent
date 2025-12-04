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
- **React Native Client**: Mobile application for iOS and Android devices
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

You have two options for LiveKit server setup:

#### Option 1: Self-hosted LiveKit Server (Recommended for Development)

For local development, you can deploy your own LiveKit server:

**Linux Installation:**
```bash
curl -sSL https://get.livekit.io | bash
```

**macOS Installation:**
```bash
brew update && brew install livekit
```

**Start Development Server:**
```bash
livekit-server --dev
```

**Default Development Credentials:**
- API key: `devkey`
- API secret: `secret`
- URL: `ws://localhost:7880`

For production deployment and custom configuration, see the [LiveKit deployment guide](https://docs.livekit.io/home/self-hosting/deployment/).

#### Option 2: LiveKit Cloud

Register for a free account at [https://cloud.livekit.io/](https://cloud.livekit.io/)

**Configure Environment (.env):**
```bash
# For local development server
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://localhost:7880

# OR for cloud deployment
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

The frontend is based on [livekit-examples/agent-starter-react](https://github.com/livekit-examples/agent-starter-react). You'll need to clone it separately:

1. **Clone the frontend repository**:
```bash
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react
```

2. **Install dependencies**:
```bash
pnpm install
```

3. **Configure LiveKit connection**:
   - Update the connection settings in the frontend to match your LiveKit server configuration
   - For local development, use the dev credentials mentioned above

4. **Run development server**:
```bash
pnpm dev
```

5. **Open your browser** and navigate to `http://localhost:3000`

### React Native Setup

For mobile development, the project provides React Native setup guidance in the `react-native/` directory. This directory contains detailed setup documentation, but you need to clone the actual React Native project:

1. **Clone the React Native project**:
```bash
git clone https://github.com/livekit-examples/agent-starter-react-native.git
cd agent-starter-react-native
```

2. **Refer to setup guidance**:
   - Check `react-native/README.md` in this project for detailed local connection procedures
   - This document contains complete steps for connecting to local LiveKit server, Token server, and Agent

3. **Install dependencies**:
```bash
bun install
```

4. **Build the project** (required before first use):
```bash
# For iOS simulator
bun expo run:ios

# For real device
bun expo run:ios --device

# For Android
bunx expo run:android
```

5. **Configure environment**:
   - Copy `.env.example` to `.env`
   - Set `EXPO_PUBLIC_TOKEN_SERVER_URL` to point to your token server
   - For different devices:
     - iOS Simulator: `http://127.0.0.1:8008/token` or host LAN IP
     - Android Simulator: `http://10.0.2.2:8008/token`
     - Real Device: Use host machine LAN IP

**Important Notes**:
- The `react-native/` directory in this project contains setup guidance documentation only
- Expo Go cannot be used - you must build the project first
- Complete setup instructions and troubleshooting guide are available in [react-native/README.md](./react-native/README.md)

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
├── react-native/                     # React Native mobile client
│   ├── README.md                     # English React Native setup guide
│   ├── README-zh.md                  # Chinese React Native setup guide
│   └── ...                          # React Native project files
├── server/                          # Token server implementation
│   ├── server.py                    # Main server implementation
│   └── ...                          # Server configuration files
└── pyproject.toml                   # Python project configuration

# Frontend (clone separately)
git clone https://github.com/livekit-examples/agent-starter-react.git
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

### Frontend Updates

To update the frontend to the latest version:

```bash
cd agent-starter-react
git pull origin main
pnpm install
pnpm dev
```

## 🔧 Network Configuration

### WSL2 Port Forwarding for LAN Access

When running the LiveKit server in WSL2, you need to configure port forwarding to allow access from other devices on the local network.

**Problem**: WSL2 uses NAT networking, so services running inside WSL2 are not accessible from other devices on the LAN, even though they're accessible from the Windows host.

**Solution**:

1. **Get WSL2 IP Address**:
```bash
hostname -I
# Example output: 172.20.10.102
```

2. **Configure Windows Port Forwarding** (run in PowerShell as Administrator):
```powershell
# Add port forwarding rules for LiveKit ports
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=7880 connectaddress=172.20.10.102 connectport=7880
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=7881 connectaddress=172.20.10.102 connectport=7881

# Verify the rules
netsh interface portproxy show all

# To delete rules (if needed):
# netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=7880
# netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=7881
```

3. **Configure Windows Firewall**:
- Open "Windows Defender Firewall with Advanced Security"
- Create Inbound Rules for TCP ports 7880 and 7881
- Allow connections for these ports

4. **Start LiveKit Server with WSL Binding**:
```bash
# Inside WSL2, start LiveKit server with proper binding
livekit-server --dev --bind 0.0.0.0
```

5. **Access from LAN Devices**:
- Get Windows host IP: `ipconfig` (look for the main network adapter)
- Access LiveKit via: `http://[Windows_Host_IP]:7880`

**Verification Steps**:
1. Check LiveKit server is listening on all interfaces: `netstat -tlnp | grep livekit`
2. Test access from Windows host: `http://localhost:7880`
3. Test access from other LAN devices using Windows IP: `http://[Windows_IP]:7880`

**Troubleshooting**:
- Ensure Windows firewall allows ports 7880 and 7881
- Check for corporate/school network restrictions
- Verify antivirus software isn't blocking connections
- Make sure WSL2 IP hasn't changed (it can change after reboot)

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

## 🎯 Additional Examples and Resources

### LiveKit Example Applications

Besides the included React frontend, you can explore these official LiveKit examples:

- **[LiveKit Meet](https://github.com/livekit-examples/meet)** - Video conferencing application similar to Zoom/Meet
- **[LiveKit Agents Examples](https://github.com/livekit/agents/tree/main/examples)** - Various voice agent implementations
- **[Spatial Audio Example](https://github.com/livekit-examples/spatial-audio)** - 3D spatial audio demonstrations

### Server Customization and Management

For advanced server setup and customization, refer to these guides:

#### Token Generation
- **[Generating Tokens](https://docs.livekit.io/home/server/generating-tokens/)** - Learn how to create authentication tokens for participants
- Custom token validation and permissions
- Room access control and security

#### Room Management
- **[Managing Rooms](https://docs.livekit.io/home/server/managing-rooms/)** - Create, configure, and manage rooms
- Room properties and configuration options
- Room lifecycle management

#### Participant Management
- **[Managing Participants](https://docs.livekit.io/home/server/managing-participants/)** - Control participant permissions and access
- Track participant state and metadata
- Handle participant events and moderation

### Server-Side Integration Examples

```python
# Example: Token generation for room access
from livekit import api

livekit_api = api.LiveKitAPI()
token = livekit_api.create_token(
    api.VideoGrant(room_join=True, room="my-room"),
    identity="user-123",
    name="Display Name"
)
```

## 🔗 Related Projects

- [LiveKit](https://livekit.io/) - Open source WebRTC infrastructure
- [AgentScope](https://github.com/modelscope/AgentScope) - Multi-agent communication framework
- [Qwen ASR](https://github.com/QwenLM/Qwen) - Alibaba's speech recognition model
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - High-quality text-to-speech synthesis
