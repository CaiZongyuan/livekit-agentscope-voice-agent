# LiveKit AgentScope 语音智能体

基于 LiveKit 的实时语音 AI 智能体，集成多种语音识别和语音合成服务提供商，并支持 AgentScope 框架。

## 🎯 功能特点

- **实时语音处理**: 低延迟的语音识别和语音合成
- **多种 TTS 服务提供商**:
  - **云端服务**: ElevenLabs、Minimax、QwenTTS
  - **本地服务**: KokoroTTS、IndexTTS 1.5（需要特定下载版本）
- **语音识别**: 通义千问 ASR 中文语音识别
- **性能监控**: 全面的指标收集和实时监控
- **双语支持**: 中英文语言能力
- **WebRTC 集成**: 基于 LiveKit 的可扩展实时通信
- **现代 Web 界面**: 基于 Next.js 的 React 前端

## 🏗️ 架构设计

### 后端 (Python)
- **语音智能体核心**: 基于 LiveKit 的智能体实现
- **自定义服务提供商**: 可扩展的语音识别和合成服务
- **指标收集**: 实时性能监控和分析
- **AgentScope 集成**: 与 AgentScope 框架的无缝集成

### 前端 (React)
- **Next.js 应用**: 用于语音交互的现代 Web 界面
- **React Native 客户端**: iOS 和 Android 移动应用
- **LiveKit 客户端 SDK**: 实时音频通信
- **响应式设计**: 基于 Tailwind CSS 和现代 React 模式

## 🚀 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+
- pnpm (用于前端依赖管理)
- uv (Python 包管理器)
- LiveKit CLI

### 后端设置

1. **克隆并设置项目**:
```bash
git clone <repository-url>
cd livekit-agentscope-voice-agent

# 使用 uv 安装依赖
uv sync

# 安装 LiveKit CLI
# 遵循官方安装指南: https://docs.livekit.io/home/cli/
# 或者通过 pip 安装（替代方法）:
pip install livekit-cli

# 复制环境模板
cp .env.example .env
# 编辑 .env 文件，填入您的 API 密钥和配置
```

2. **配置 LiveKit 环境**:

您有两种 LiveKit 服务器设置选项：

#### 选项 1：自托管 LiveKit 服务器（推荐用于开发）

对于本地开发，您可以部署自己的 LiveKit 服务器：

**Linux 安装：**
```bash
curl -sSL https://get.livekit.io | bash
```

**macOS 安装：**
```bash
brew update && brew install livekit
```

**启动开发服务器：**
```bash
livekit-server --dev
```

**默认开发凭据：**
- API 密钥: `devkey`
- API 密码: `secret`
- URL: `ws://localhost:7880`

有关生产部署和自定义配置，请参阅 [LiveKit 部署指南](https://docs.livekit.io/home/self-hosting/deployment/)。

#### 选项 2：LiveKit 云服务

在 [https://cloud.livekit.io/](https://cloud.livekit.io/) 注册免费账户

**配置环境 (.env)：**
```bash
# 本地开发服务器
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://localhost:7880

# 或云部署
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.url
```

3. **运行语音智能体**:
```bash
# 基础版本
uv run agent_server_demo.py start

# 带性能监控的版本
uv run agent_server_with_metrics.py start
```

### 前端设置

前端基于 [livekit-examples/agent-starter-react](https://github.com/livekit-examples/agent-starter-react)，您需要单独克隆：

1. **克隆前端仓库**:
```bash
git clone https://github.com/livekit-examples/agent-starter-react.git
cd agent-starter-react
```

2. **安装依赖**:
```bash
pnpm install
```

3. **配置 LiveKit 连接**:
   - 更新前端中的连接设置以匹配您的 LiveKit 服务器配置
   - 本地开发时使用上述提到的开发凭据

4. **运行开发服务器**:
```bash
pnpm dev
```

5. **打开浏览器** 访问 `http://localhost:3000`

### React Native 移动端设置

项目提供了 React Native 移动客户端的设置指导，位于 `react-native/` 目录中。该目录包含详细的设置文档，但您需要克隆实际的 React Native 项目：

1. **克隆 React Native 项目**:
```bash
git clone https://github.com/livekit-examples/agent-starter-react-native.git
cd agent-starter-react-native
```

2. **参考设置指导**:
   - 查看本项目中的 `react-native/README-zh.md` 获取详细的本地连接流程
   - 该文档包含如何连接本地 LiveKit 服务器、Token 服务器和 Agent 的完整步骤

3. **安装依赖**:
```bash
bun install
```

4. **构建项目**（首次使用前必须进行）:
```bash
# iOS 模拟器
bun expo run:ios

# 真机设备
bun expo run:ios --device

# Android 设备
bunx expo run:android
```

5. **配置环境**:
   - 复制 `.env.example` 到 `.env`
   - 设置 `EXPO_PUBLIC_TOKEN_SERVER_URL` 指向您的令牌服务器
   - 不同设备的 IP 配置：
     - iOS 模拟器：`http://127.0.0.1:8008/token` 或主机局域网 IP
     - Android 模拟器：`http://10.0.2.2:8008/token`
     - 真机设备：使用主机局域网 IP

**重要提示**:
- 本项目的 `react-native/` 目录仅包含设置指导文档
- 不能使用 Expo Go - 必须先构建项目
- 完整的设置说明和故障排除指南请参考 [react-native/README-zh.md](./react-native/README-zh.md)

## ⚙️ 配置说明

### 环境变量

`.env` 文件中必需的环境变量：

```env
# 语言模型
DEEPSEEK_API_KEY=your_deepseek_api_key

# 语音服务
ELEVEN_API_KEY=your_elevenlabs_api_key
MINIMAX_API_KEY=your_minimax_api_key
DASHSCOPE_API_KEY=your_qwen_asr_api_key

# LiveKit 配置
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.url
```

### 语音服务提供商配置

#### 通义千问 ASR (中文语音识别)
- 模型: `qwen3-asr-flash`
- 语言: `zh` (中文)
- 特性: 逆文本规范化、流式支持

#### TTS 服务提供商

##### 云端 TTS
1. **ElevenLabs TTS**: 高质量语音合成，支持多种语音选项
   - API 密钥: `ELEVEN_API_KEY`
   - 自然语音，情感表达丰富

2. **Minimax TTS**: 云端中英文合成服务
   - API 密钥: `MINIMAX_API_KEY`
   - 模型: `speech-2.6-hd`，多种语音选项
   - 强大的中文支持

3. **Qwen TTS**: 阿里巴巴文本转语音服务
   - API 密钥: `DASHSCOPE_API_KEY` (与 ASR 共用)
   - 针对中文优化

##### 本地 TTS

1. **Kokoro TTS**: 本地合成引擎
   - **下载地址**: [Kokoro TTS 安装包](https://pan.quark.cn/s/77eb46560914)
   - **参考教程**: [B站设置教程](https://www.bilibili.com/video/BV1ziuBzyEjF/)
   - **接口格式**: `http://localhost:9880/?text={文本}&speaker={音频路径}&speed=1.0`
   - **默认说话人**:
     - `speaker_en=am_adam_男.pt`
     - `speaker_zh=zm_029.pt`
   - 无需网络连接
   - 快速推理速度

2. **Index-TTS-v1.5**: 增强型并发本地 TTS
   - **下载地址**: [Index-TTS-v1.5 安装包](https://pan.quark.cn/s/d3d521cccf91)
   - **批量任务**: [批量任务文件](https://pan.quark.cn/s/eb3d65587e6b)
   - **参考教程**: [B站设置教程](https://www.bilibili.com/video/BV1RkT2zREHs)
   - **接口格式**: `http://localhost:9880/?text={文本}&speaker={语音模型}&volume=1.9`
   - **特性**:
     - 并发处理（解决多设备请求崩溃问题）
     - 音量控制
     - 批量任务支持
     - API 接口支持
     - 支持 RTX 50 系列显卡
     - 4G 显存可用
   - 高质量语音合成
   - 自定义语音模型支持

3. **FishSpeech 1.5.1**: 备选本地 TTS 方案
   - **下载地址**: [FishSpeech 安装包](https://pan.quark.cn/s/bc0db941ebda)
   - **参考教程**: [B站设置教程](https://www.bilibili.com/video/BV1YrYjzNEHf)
   - **接口格式**: `http://localhost:9880?text={文本}&speaker={语音描述}`
   - **注意**: 需要根据视频教程自行实现 provider
   - 高质量女声支持
   - 设置说明在 `providers/` 目录中

## 📊 监控与指标

智能体包含全面的性能监控功能：

- **LLM 指标**: Token 使用量、处理速度、首字节时间
- **STT 指标**: 识别延迟、实时因子、流式性能
- **TTS 指标**: 首字节延迟、合成时间、音频时长
- **EOU 指标**: 语句结束检测性能

指标会发送到 WebSocket 监控服务器，并输出到控制台用于调试。

## 🛠️ 开发

### 项目结构

```
livekit-agentscope-voice-agent/
├── agent_server_demo.py              # 基础语音智能体实现
├── agent_server_with_metrics.py      # 带性能监控的智能体
├── providers/                        # 自定义语音服务提供商实现
│   ├── qwen_asr_stt.py              # 通义千问语音识别服务
│   ├── kokoro_tts.py                # Kokoro 语音合成服务
│   ├── local_indexTTS.py            # 本地 Index TTS 服务
│   └── local_indextts_chaos.py      # 备用本地 TTS 服务
├── react-native/                     # React Native 移动客户端
│   ├── README.md                     # 英文 React Native 设置指南
│   ├── README-zh.md                  # 中文 React Native 设置指南
│   └── ...                          # React Native 项目文件
├── server/                          # 令牌服务器实现
│   ├── server.py                    # 主服务器实现
│   └── ...                          # 服务器配置文件
└── pyproject.toml                   # Python 项目配置

# 前端（需要单独克隆）
git clone https://github.com/livekit-examples/agent-starter-react.git
```

### 添加自定义服务提供商

1. **在 `providers/` 目录中创建新的服务提供商**
2. **继承相应的 LiveKit 基类**:
   - `stt.STT` 用于语音识别
   - `tts.TTS` 用于语音合成
3. **实现必需的方法** 并处理身份验证
4. **如需性能监控，添加指标收集**
5. **更新智能体配置** 以使用您的新的服务提供商

### 运行测试

```bash
# Python 测试（如果已实现）
pytest

# 前端测试
cd agent-starter-react
pnpm test
```

### 生产环境构建

```bash
# 后端
uv sync --production

# 前端
cd agent-starter-react
pnpm build
pnpm start
```

### 前端更新

要将前端更新到最新版本：

```bash
cd agent-starter-react
git pull origin main
pnpm install
pnpm dev
```

## 🔧 网络配置

### WSL2 局域网访问端口转发

在 WSL2 中运行 LiveKit 服务器时，需要配置端口转发以允许局域网内其他设备访问。

**问题**: WSL2 使用 NAT 网络，因此在 WSL2 内运行的服务无法从局域网的其他设备访问，即使从 Windows 主机可以访问。

**解决方案**:

1. **获取 WSL2 IP 地址**:
```bash
hostname -I
# 示例输出: 172.20.10.102
```

2. **配置 Windows 端口转发**（以管理员身份运行 PowerShell）:
```powershell
# 为 LiveKit 端口添加端口转发规则
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=7880 connectaddress=172.20.10.102 connectport=7880
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=7881 connectaddress=172.20.10.102 connectport=7881

# 验证规则
netsh interface portproxy show all

# 如需删除规则：
# netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=7880
# netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=7881
```

3. **配置 Windows 防火墙**:
- 打开"Windows Defender 防火墙高级安全"
- 为 TCP 端口 7880 和 7881 创建入站规则
- 允许这些端口的连接

4. **在 WSL 中绑定所有接口启动 LiveKit 服务器**:
```bash
# 在 WSL2 内部，启动 LiveKit 服务器并绑定到所有接口
livekit-server --dev --bind 0.0.0.0
```

5. **从局域网设备访问**:
- 获取 Windows 主机 IP: `ipconfig`（查找主网络适配器）
- 通过以下方式访问 LiveKit: `http://[Windows_Host_IP]:7880`

**验证步骤**:
1. 检查 LiveKit 服务器是否在所有接口上监听: `netstat -tlnp | grep livekit`
2. 从 Windows 主机测试访问: `http://localhost:7880`
3. 从其他局域网设备使用 Windows IP 测试访问: `http://[Windows_IP]:7880`

**故障排除**:
- 确保 Windows 防火墙允许端口 7880 和 7881
- 检查企业/学校网络限制
- 验证杀毒软件没有阻止连接
- 确保 WSL2 IP 没有变化（重启后可能会变化）

## 🌐 部署

### 后端部署

1. **部署到云服务器** 或使用 Docker 容器化
2. **为生产环境配置环境变量**
3. **设置 LiveKit 服务器**（云端或自托管）
4. **配置监控服务器** 用于指标收集

### 前端部署

```bash
cd agent-starter-react
pnpm build
# 将 .next 目录部署到您的托管平台
```

## 🤝 贡献

1. Fork 该仓库
2. 创建功能分支
3. 进行您的更改
4. 如适用，添加测试
5. 提交拉取请求

## 📝 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

## 🎯 更多示例和资源

### LiveKit 示例应用程序

除了包含的 React 前端，您还可以探索这些官方 LiveKit 示例：

- **[LiveKit Meet](https://github.com/livekit-examples/meet)** - 类似 Zoom/Meet 的视频会议应用
- **[LiveKit Agents 示例](https://github.com/livekit/agents/tree/main/examples)** - 各种语音智能体实现
- **[空间音频示例](https://github.com/livekit-examples/spatial-audio)** - 3D 空间音频演示

### 服务器自定义和管理

有关高级服务器设置和自定义，请参阅以下指南：

#### 令牌生成
- **[生成令牌](https://docs.livekit.io/home/server/generating-tokens/)** - 学习如何为参与者创建身份验证令牌
- 自定义令牌验证和权限
- 房间访问控制和安全

#### 房间管理
- **[管理房间](https://docs.livekit.io/home/server/managing-rooms/)** - 创建、配置和管理房间
- 房间属性和配置选项
- 房间生命周期管理

#### 参与者管理
- **[管理参与者](https://docs.livekit.io/home/server/managing-participants/)** - 控制参与者权限和访问
- 跟踪参与者状态和元数据
- 处理参与者和事件审核

### 服务器端集成示例

```python
# 示例：为房间访问生成令牌
from livekit import api

livekit_api = api.LiveKitAPI()
token = livekit_api.create_token(
    api.VideoGrant(room_join=True, room="my-room"),
    identity="user-123",
    name="显示名称"
)
```

## 🔗 相关项目

- [LiveKit](https://livekit.io/) - 开源 WebRTC 基础设施
- [AgentScope](https://github.com/modelscope/AgentScope) - 多智能体通信框架
- [Qwen ASR](https://github.com/QwenLM/Qwen) - 阿里巴巴语音识别模型
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - 高质量文本转语音合成

