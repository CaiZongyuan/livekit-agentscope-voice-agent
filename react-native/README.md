# React Native Local LiveKit Service Connection Process

**English | [中文](./README-zh.md)**

A reproducible set of steps to run locally, focusing on enabling the React Native client to connect to your LiveKit + Token Server + Agent.

## Project Source

This project is based on cloning and modifying [LiveKit React Native Agent Starter](https://github.com/livekit-examples/agent-starter-react-native).

For complete documentation, refer to: [LiveKit React Native Quick Start](https://docs.livekit.io/home/quickstarts/react-native/)

## Prerequisites

Before starting, ensure your development environment is properly configured:

- Node.js 18+
- React Native development environment (Expo CLI)
- iOS development environment (Xcode) - Required only for iOS development
- Android Studio - Required only for Android development

## Build Project

You need to build the project before first use:

```bash
# Install dependencies
bun install

# Use iOS simulator
bun expo run:ios

# Use real device
bun expo run:ios --device
```

**Note:** You must complete the build steps to run the application normally. Expo Go cannot be used.

## 1) Start LiveKit Server
- Command: `livekit-server --dev --bind 0.0.0.0 --port 7880`
- Purpose: Open signaling port 7880 to the LAN for mobile/simulator access.
- Verification: On Mac, `lsof -i :7880` should show a process; mobile/simulator browser accessing `http://<yourIP>:7880` should not be rejected.

## 2) Configure and Start Token Server
Edit `livekit-agentscope-voice-agent/.env`:
```
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://<yourIP>:7880   # e.g., ws://192.168.2.199:7880
PORT=8008
```
Start with:
```
uv run server/server.py
```
Verification: `curl http://<yourIP>:8008/token` returns 200 (you can ignore 422 validation failure, just check if it can connect).

## 3) Start Agent
- Command: `uv run python agent_server_demo.py start`
- Note: The worker health check port is fixed to 8083 in the code. The `registered worker` in the startup log should show `url` as your LAN IP, not localhost.

## 4) Configure React Native Client
In `agent-starter-react-native/.env`:
```
EXPO_PUBLIC_TOKEN_SERVER_URL=http://<yourIP>:8008/token
```
How to fill `<yourIP>` for different devices:
- iOS Simulator: `http://127.0.0.1:8008/token` or host machine LAN IP.
- Android Simulator: `http://10.0.2.2:8008/token`.
- Real Device: Use host machine LAN IP (same IP as LIVEKIT_URL).

Restart Expo/Metro after changes (stop completely and restart) to make environment variables take effect.

## 5) Run React Native
- First `bun install` (or if dependencies are already installed).
- Start with: `bunx expo run:ios` or `bunx expo run:android`.
- In the app, click "Start voice assistant", which will POST `{room, identity, name, auto_create_room:true}` to the Token Server, get `{token,url,room}` and connect.

## Common Connectivity Checks
- Agent/Token Server still shows `ws://localhost:7880`: Indicates `.env` IP wasn't changed or process wasn't restarted.
- "Network request failed" / "Connection refused": Mostly LiveKit 7880 isn't started, not bound to 0.0.0.0, or firewall/routing unreachable; first verify by accessing `http://<IP>:7880` from device side using browser/curl.
- event-target-shim WARN: Package export warning, doesn't affect network, ignore it.

## Changes to `hooks/useConnection.tsx` Explanation
- Added `EXPO_PUBLIC_TOKEN_SERVER_URL` support: If configured, use `TokenSource.custom` to request Token Server, POST `{room, identity, name, auto_create_room:true}`, read returned `{token, url, room}` as connection info.
- Retained original `sandboxID` (LiveKit Sandbox Token Server) and hardcoded token modes; can still be used when token server is not configured.
- Support environment variable injection for manual token: `EXPO_PUBLIC_LIVEKIT_URL`, `EXPO_PUBLIC_PARTICIPANT_TOKEN`.
- When connecting, randomly generate `roomName/identity` on client side, and use `url` returned by Token Server as signaling address, avoiding client/server URL inconsistency.