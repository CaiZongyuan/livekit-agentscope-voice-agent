# LiveKit Token 认证与房间分配指南

## 概述

本文档详细说明了 LiveKit AgentScope Voice Agent 项目中 Token 认证机制和房间分配的完整流程。Token Server 负责身份验证和权限管理，LiveKit Server 负责实际的音视频传输。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    前端客户端     │    │  Token Server   │   │  LiveKit Server  │
│   (React/RN)    │    │   (server.py)   │    │    (7880端口)    │
│                 │    │    (8008端口)    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. 请求 Token          │                       │
         │---------------------->│                       │
         │                       │ 2. 生成 JWT Token      │
         │                       │  - 使用 API_KEY 签名   │
         │                       │  - 分配房间权限        │
         │                       │                       │
         │ 3. 返回 Token + 房间名 │                       │
         │<----------------------│                       │
         │                       │                       │
         │ 4. 携带 Token 连接     │                       │
         │---------------------------------------------->│
         │                       │                       │
         │                       │                       │ 5. 验证 Token
         │                       │                       │    - 检查签名
         │                       │                       │    - 验证房间权限
         │                       │                       │    - 确认有效期
         │                       │                       │
         │                       │                       │ 6. 建立连接
         │<----------------------------------------------│
```

## JWT Token 结构

### Header (头部)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload (数据载荷)
```json
{
  "video": {
    "roomJoin": true,
    "room": "voice_assistant_room_12345",
    "canPublish": true,
    "canSubscribe": true,
    "canPublishData": true
  },
  "sub": "user_12345",
  "iss": "devkey",
  "nbf": 1703952000,
  "exp": 1703952000
}
```

### Signature (签名)
使用 API_SECRET 对 Header + Payload 进行 HMACSHA256 签名，确保 Token 不可篡改。

## Token 生成流程

### 1. Token Server 端点实现

```python
# livekit-agentscope-voice-agent/server/server.py

@app.post("/token")
async def get_token(body: TokenRequest):
    # 验证配置
    _require_config()

    # 自动创建房间（如果需要）
    if body.auto_create_room:
        await _ensure_room(body.room)

    # 定义权限
    grants = api.VideoGrants(
        room_join=True,
        room=body.room,           # 绑定到特定房间
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )

    # 生成 Token
    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(body.identity)
        .with_name(body.name or body.identity)
        .with_grants(grants)
    )

    return {
        "token": token.to_jwt(),
        "url": LIVEKIT_URL,
        "identity": body.identity,
        "room": body.room,
    }
```

### 2. Token 请求格式

```json
POST /token
Content-Type: application/json

{
    "room": "voice_assistant_room_12345",
    "identity": "user_12345",
    "name": "张三",
    "auto_create_room": true
}
```

### 3. Token 响应格式

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "url": "ws://192.168.2.30:7880",
    "identity": "user_12345",
    "room": "voice_assistant_room_12345"
}
```

## 房间分配机制

### 房间命名策略

可以在客户端生成随机房间名与 identity：

```python
import random

# 生成唯一房间名
room_name = f"voice_assistant_room_{random.randint(10000, 99999)}"
participant_identity = f"user_{random.randint(10000, 99999)}"
```

> 说明：服务端不会自动生成房间名或 identity，需由客户端调用 `/token` 时传入 `room` 与 `identity`。

### 房间自动创建

```python
async def _ensure_room(room_name: str):
    """如果房间不存在则自动创建"""
    try:
        async with api.LiveKitAPI() as lkapi:
            await lkapi.room.create_room(api.CreateRoomRequest(
                name=room_name,
            ))
    except Exception as exc:
        # 房间已存在是正常情况
        if "already exists" in str(exc).lower():
            return
        raise HTTPException(status_code=500, detail=f"创建房间失败: {exc}")
```

### 权限控制

Token 中的 `video` 字段严格限制用户权限（字段均为驼峰形式）：

- `roomJoin`: 是否允许加入房间
- `room`: 只能加入指定的房间名
- `canPublish`: 是否允许发布音视频流
- `canSubscribe`: 是否允许订阅音视频流
- `canPublishData`: 是否允许发送数据消息

## LiveKit Server 验证机制

### 验证流程

1. **解析 Token**: 提取 Header、Payload、Signature
2. **验证签名**: 使用存储的 API_SECRET 验证 Token 签名
3. **检查权限**: 验证 Token 是否有权限加入请求的房间
4. **检查有效期**: 确认 Token 未过期
5. **建立连接**: 允许用户加入房间并开始音视频传输

### 密钥管理

```python
# Token Server 配置
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")      # "devkey"
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET") # "secret"

# LiveKit Server 配置 (livekit.yaml)
keys:
  - key_id: "devkey"
    api_secret: "secret"
```

## 客户端集成

### React 客户端示例

```typescript
// 前端直接向 Token Server 请求
const response = await fetch('http://localhost:8008/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    room: 'voice_assistant_room_12345',
    identity: 'user_12345',
    name: '张三',
    auto_create_room: true,
  })
});

const { url, room, token } = await response.json();

// 使用 Token 连接
const room = new Room(options);
await room.connect(url, token);
```

### React Native 客户端示例

```typescript
// React Native 直接调用 Token Server
const getConnectionDetails = async () => {
  const response = await fetch('http://localhost:8008/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      room: 'room_name',
      identity: 'user_identity',
      name: 'User Name',
      auto_create_room: true
    })
  });

  const { token, url, room } = await response.json();
  return { token, url, room };
};
```

## Agent 连接同一房间

Agent 需要获取同一房间的 Token 才能与用户通信：

### 方式一：使用相同 Token Server

```python
# Agent 请求同一房间的 Token
agent_response = requests.post("http://localhost:8008/token", json={
    "room": "voice_assistant_room_12345",  # 指定相同房间
    "identity": "agent_bot",
    "name": "语音助手"
})

agent_token = agent_response.json()["token"]
```

### 方式二：直接生成 Token（如果有 API 权限）

```python
# Agent 直接生成 Token
from livekit import api

agent_token = (
    api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    .with_identity("agent_bot")
    .with_name("语音助手")
    .with_grants(api.VideoGrants(
        room="voice_assistant_room_12345",  # 指定同一房间
        room_join=True,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    .to_jwt()
)
```

## 安全注意事项

### 1. 密钥保护
- API_KEY 和 API_SECRET 必须安全存储
- 不要在前端代码中暴露密钥
- 使用环境变量管理敏感信息

### 2. Token 时效性
- Token 设置合理的过期时间（建议 15 分钟）
- 及时清理过期 Token

### 3. 权限最小化
- 只授予必要的权限
- 限制 Token 只能访问特定房间

### 4. 房间生命周期
- 设置合理的 `empty_timeout`
- 自动清理无人房间

## 部署配置

### 环境变量配置

```bash
# .env 文件
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://192.168.2.30:7880
PORT=8008
```

### 启动服务

```bash
# 启动 Token Server
cd /path/to/livekit-agentscope-voice-agent
python server/server.py

# Token Server 将在 http://localhost:8008 启动
# 主要端点：
# - POST /token - 获取连接 Token
# - POST /rooms - 创建房间
# - GET /health - 健康检查
```

## 故障排查

### 常见错误

1. **Token 验证失败**
   - 检查 API_KEY 和 API_SECRET 是否正确
   - 确认 LiveKit Server 和 Token Server 使用相同的密钥

2. **房间权限错误**
   - 检查 Token 中的 room 字段是否匹配请求的房间
   - 确认 Token 包含 room_join 权限

3. **Token 过期**
   - 检查 Token 的 exp 字段
   - 调整 Token 有效期

### 调试技巧

```python
# 解码 Token 用于调试
import jwt

def decode_token(token):
    # 只解码，不验证签名（仅用于调试）
    payload = jwt.decode(token, options={"verify_signature": False})
    print("Token 内容:", payload)

# 检查 Token 权限
def check_token_permissions(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    grants = payload.get("video", {})
    print("房间权限:", grants)
    print("允许加入:", grants.get("roomJoin"))
    print("目标房间:", grants.get("room"))
```

## 总结

Token 认证机制为 LiveKit 提供了安全的身份验证和权限管理：

1. **身份验证**: 通过数字签名确保 Token 真实性
2. **权限控制**: 精确控制用户能做什么操作
3. **房间隔离**: 每个 Token 只能访问指定房间
4. **时效性**: Token 自动过期，提高安全性
5. **可扩展性**: 支持 Web 和移动应用的统一认证

正确配置和使用 Token 认证是构建安全可靠的实时音视频应用的关键。
