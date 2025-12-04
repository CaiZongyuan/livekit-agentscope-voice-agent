# LiveKit Token Authentication and Room Assignment Guide

**English | [中文](./README-zh.md)**

## Overview

This document provides a detailed explanation of the complete Token authentication mechanism and room assignment process in the LiveKit AgentScope Voice Agent project. The Token Server is responsible for authentication and permission management, while the LiveKit Server handles actual audio/video transmission.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Token Server   │    │  LiveKit Server │
│   Client        │    │   (server.py)   │    │    (port 7880)  │
│   (React/RN)    │    │   (port 8008)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Request Token     │                       │
         │--------------------->│                       │
         │                       │ 2. Generate JWT Token │
         │                       │  - Sign with API_KEY  │
         │                       │  - Assign room perms  │
         │                       │                       │
         │ 3. Return Token +    │                       │
         │    Room Name         │                       │
         │<---------------------│                       │
         │                       │                       │
         │ 4. Connect with      │                       │
         │    Token             │---------------------->│
         │                       │                       │
         │                       │                       │ 5. Verify Token
         │                       │                       │    - Check signature
         │                       │                       │    - Verify room perms
         │                       │                       │    - Confirm expiry
         │                       │                       │
         │                       │                       │ 6. Establish
         │                       │                       │    Connection
         │<-----------------------------------------------│
```

## JWT Token Structure

### Header
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload
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

### Signature
Uses HMAC-SHA256 signature with API_SECRET on Header + Payload to ensure Token cannot be tampered with.

## Token Generation Process

### 1. Token Server Endpoint Implementation

```python
# livekit-agentscope-voice-agent/server/server.py

@app.post("/token")
async def get_token(body: TokenRequest):
    # Verify configuration
    _require_config()

    # Auto-create room if needed
    if body.auto_create_room:
        await _ensure_room(body.room)

    # Define permissions
    grants = api.VideoGrants(
        room_join=True,
        room=body.room,           # Bind to specific room
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
    )

    # Generate Token
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

### 2. Token Request Format

```json
POST /token
Content-Type: application/json

{
    "room": "voice_assistant_room_12345",
    "identity": "user_12345",
    "name": "John Doe",
    "auto_create_room": true
}
```

### 3. Token Response Format

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "url": "ws://192.168.2.30:7880",
    "identity": "user_12345",
    "room": "voice_assistant_room_12345"
}
```

## Room Assignment Mechanism

### Room Naming Strategy

You can generate random room names and identity on the client side:

```python
import random

# Generate unique room name
room_name = f"voice_assistant_room_{random.randint(10000, 99999)}"
participant_identity = f"user_{random.randint(10000, 99999)}"
```

> Note: The server does not automatically generate room names or identity. These must be passed by the client when calling `/token` with `room` and `identity` parameters.

### Automatic Room Creation

```python
async def _ensure_room(room_name: str):
    """Auto-create room if it doesn't exist"""
    try:
        async with api.LiveKitAPI() as lkapi:
            await lkapi.room.create_room(api.CreateRoomRequest(
                name=room_name,
            ))
    except Exception as exc:
        # Room already existing is normal
        if "already exists" in str(exc).lower():
            return
        raise HTTPException(status_code=500, detail=f"Failed to create room: {exc}")
```

### Permission Control

The `video` field in the Token strictly restricts user permissions (all fields use camelCase):

- `roomJoin`: Whether to allow joining the room
- `room`: Can only join the specified room name
- `canPublish`: Whether to allow publishing audio/video streams
- `canSubscribe`: Whether to allow subscribing to audio/video streams
- `canPublishData`: Whether to allow sending data messages

## LiveKit Server Verification Mechanism

### Verification Process

1. **Parse Token**: Extract Header, Payload, Signature
2. **Verify Signature**: Use stored API_SECRET to verify Token signature
3. **Check Permissions**: Verify Token has permission to join requested room
4. **Check Validity**: Confirm Token is not expired
5. **Establish Connection**: Allow user to join room and start audio/video transmission

### Key Management

```python
# Token Server Configuration
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")      # "devkey"
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET") # "secret"

# LiveKit Server Configuration (livekit.yaml)
keys:
  - key_id: "devkey"
    api_secret: "secret"
```

## Client Integration

### React Client Example

```typescript
// Frontend directly requests from Token Server
const response = await fetch('http://localhost:8008/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    room: 'voice_assistant_room_12345',
    identity: 'user_12345',
    name: 'John Doe',
    auto_create_room: true,
  })
});

const { url, room, token } = await response.json();

// Connect using Token
const room = new Room(options);
await room.connect(url, token);
```

### React Native Client Example

```typescript
// React Native directly calls Token Server
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

## Agent Connecting to the Same Room

The Agent needs to get a Token for the same room to communicate with users:

### Method 1: Use Same Token Server

```python
# Agent requests Token for the same room
agent_response = requests.post("http://localhost:8008/token", json={
    "room": "voice_assistant_room_12345",  # Specify same room
    "identity": "agent_bot",
    "name": "Voice Assistant"
})

agent_token = agent_response.json()["token"]
```

### Method 2: Direct Token Generation (if API permissions available)

```python
# Agent directly generates Token
from livekit import api

agent_token = (
    api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    .with_identity("agent_bot")
    .with_name("Voice Assistant")
    .with_grants(api.VideoGrants(
        room="voice_assistant_room_12345",  # Specify same room
        room_join=True,
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True
    ))
    .to_jwt()
)
```

## Security Considerations

### 1. Key Protection
- API_KEY and API_SECRET must be stored securely
- Do not expose keys in frontend code
- Use environment variables to manage sensitive information

### 2. Token Validity
- Set reasonable expiration time for Tokens (recommended 15 minutes)
- Clean up expired Tokens promptly

### 3. Minimum Privilege
- Only grant necessary permissions
- Restrict Tokens to access only specific rooms

### 4. Room Lifecycle
- Set reasonable `empty_timeout`
- Automatically clean up empty rooms

## Deployment Configuration

### Environment Variables Configuration

```bash
# .env file
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://192.168.2.30:7880
PORT=8008
```

### Starting Services

```bash
# Start Token Server
cd /path/to/livekit-agentscope-voice-agent
python server/server.py

# Token Server will start at http://localhost:8008
# Main endpoints:
# - POST /token - Get connection Token
# - POST /rooms - Create room
# - GET /health - Health check
```

## Troubleshooting

### Common Errors

1. **Token Verification Failed**
   - Check if API_KEY and API_SECRET are correct
   - Confirm LiveKit Server and Token Server use the same keys

2. **Room Permission Error**
   - Check if room field in Token matches requested room
   - Confirm Token includes room_join permission

3. **Token Expired**
   - Check exp field in Token
   - Adjust Token validity period

### Debugging Tips

```python
# Decode Token for debugging
import jwt

def decode_token(token):
    # Decode only, don't verify signature (debug only)
    payload = jwt.decode(token, options={"verify_signature": False})
    print("Token content:", payload)

# Check Token permissions
def check_token_permissions(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    grants = payload.get("video", {})
    print("Room permissions:", grants)
    print("Can join:", grants.get("roomJoin"))
    print("Target room:", grants.get("room"))
```

## Summary

The Token authentication mechanism provides secure identity verification and permission management for LiveKit:

1. **Identity Verification**: Ensure Token authenticity through digital signatures
2. **Permission Control**: Precise control over what users can do
3. **Room Isolation**: Each Token can only access specified rooms
4. **Timeliness**: Tokens automatically expire for increased security
5. **Scalability**: Support unified authentication for web and mobile applications

Proper configuration and use of Token authentication is key to building secure and reliable real-time audio/video applications.