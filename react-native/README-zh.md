# React Native 连接本地 LiveKit 服务流程

一套可复现的本地跑通步骤，重点是让 React Native 端能连上你的 LiveKit + Token Server + Agent。

## 项目来源

本项目基于 [LiveKit React Native Agent Starter](https://github.com/livekit-examples/agent-starter-react-native) 克隆和修改。

完整文档请参考：[LiveKit React Native 快速开始](https://docs.livekit.io/home/quickstarts/react-native/)

## 前置要求

在开始之前，请确保你的开发环境已配置好：

- Node.js 18+
- React Native 开发环境 (Expo CLI)
- iOS 开发环境 (Xcode) - 仅 iOS 开发需要
- Android Studio - 仅 Android 开发需要

## 构建项目

首次使用前需要构建项目：

```bash
# 安装依赖
bun install

# 使用ios模拟器
bun expo run:ios

# 使用真机
bun expo run:ios --device
```

**注意：** 必须完成构建步骤才能正常运行应用程序，无法使用 expo go。

## 1) 启动 LiveKit Server
- 命令：`livekit-server --dev --bind 0.0.0.0 --port 7880`
- 作用：对局域网开放 7880 信令口，便于手机/模拟器访问。
- 验证：在 Mac 上 `lsof -i :7880` 应有进程；手机/模拟器浏览器访问 `http://<你的IP>:7880` 不应被拒绝。

## 2) 配置并启动 Token Server
编辑 `livekit-agentscope-voice-agent/.env`：
```
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://<你的IP>:7880   # 例如 ws://192.168.2.199:7880
PORT=8008
```
启动：
```
uv run server/server.py
```
验证：`curl http://<你的IP>:8008/token` 返回 200（可忽略 422 验证失败，只看是否能连通）。

## 3) 启动 Agent
- 命令：`uv run python agent_server_demo.py start`
- 说明：已在代码中将 worker 健康检查端口固定为 8083。启动日志中的 `registered worker` 应该显示 `url` 为你的内网 IP，而非 localhost。

## 4) 配置 React Native 客户端
在 `agent-starter-react-native/.env`：
```
EXPO_PUBLIC_TOKEN_SERVER_URL=http://<你的IP>:8008/token
```
设备如何填写 `<你的IP>`：
- iOS 模拟器：`http://127.0.0.1:8008/token` 或宿主机局域网 IP。
- Android 模拟器：`http://10.0.2.2:8008/token`。
- 真机：用宿主机局域网 IP（与 LiveKit_URL 相同的 IP）。

改完后重启 Expo/Metro（完全停止再启动），让环境变量生效。

## 5) 运行 React Native
- 先 `bun install`（或现有依赖已装好）。
- 启动：`bunx expo run:ios` 或 `bunx expo run:android`。
- 在应用里点击 “Start voice assistant”，会向 Token Server POST `{room, identity, name, auto_create_room:true}`，拿到 `{token,url,room}` 并连接。

## 常见连通性检查
- Agent/Token Server 仍显示 `ws://localhost:7880`：说明 `.env` 未改 IP 或进程没重启。
- “Network request failed” / “Connection refused”：多半 LiveKit 7880 未启动、未绑定 0.0.0.0，或防火墙/路由不可达；先用浏览器/curl 从设备侧访问 `http://<IP>:7880` 验证。
- event-target-shim WARN：包导出警告，不影响网络，忽略即可。***

## 对于 `hooks/useConnection.tsx` 的改动说明
- 新增 `EXPO_PUBLIC_TOKEN_SERVER_URL` 支持：若配置，则用 `TokenSource.custom` 请求 Token Server，POST `{room, identity, name, auto_create_room:true}`，读取返回的 `{token, url, room}` 作为连接信息。
- 保留原有 `sandboxID`（LiveKit Sandbox Token Server）和硬编码 token 模式；未配置 token server 时仍可使用。
- 支持环境变量注入手动 token：`EXPO_PUBLIC_LIVEKIT_URL`、`EXPO_PUBLIC_PARTICIPANT_TOKEN`。
- 连接时在客户端随机生成 `roomName/identity`，并使用 Token Server 返回的 `url` 作为信令地址，避免客户端/服务端 URL 不一致。
