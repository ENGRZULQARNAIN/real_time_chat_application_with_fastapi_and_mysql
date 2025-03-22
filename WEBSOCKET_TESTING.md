# WebSocket Testing Guide

This document explains how to test the WebSocket functionality of the Real Time Chat Application.

## Testing with HTML Test Client

A simple HTML WebSocket client is provided in `backend/websocket_test.html` for testing outside of Postman.

### How to Use the HTML Client

1. Open `backend/websocket_test.html` in your browser
2. Enter the WebSocket server URL (default: `ws://localhost:8000/ws/`)
3. Enter the room ID you want to connect to
4. Paste your JWT token in the Authentication Token field
5. Click "Connect"
6. Once connected, you can send and receive messages in real-time

### Testing Multiple Users

To test chat between multiple users:

1. Open the HTML client in two different browser windows
2. Log in with different user accounts in each window
3. Connect both clients to the same chat room
4. Send messages from either client to see them appear in both windows

## WebSocket Message Format

The WebSocket API uses JSON for all messages. Here are the message formats:

### Messages Sent from Client to Server

```json
{
  "text": "Your message text here"
}
```

### Messages Received from Server

1. User Joined Event:

```json
{
  "type": "user_joined",
  "user_id": 123,
  "user_name": "John Doe",
  "room_id": 1,
  "active_users": [123, 456]
}
```

2. User Left Event:

```json
{
  "type": "user_left",
  "user_id": 456,
  "user_name": "Jane Smith",
  "room_id": 1,
  "active_users": [123]
}
```

3. Chat Message:

```json
{
  "type": "message",
  "id": 789,
  "text": "Hello world!",
  "sender_id": 123,
  "sender_name": "John Doe",
  "room_id": 1,
  "created_at": "2023-03-22T12:34:56.789Z"
}
```

4. Error:

```json
{
  "error": "Error message"
}
```

## Troubleshooting

1. **Connection Failed**: Make sure your JWT token is valid and not expired
2. **Authentication Error**: Ensure you've joined the chat room first using the REST API
3. **Can't Send Messages**: Check if your WebSocket connection is still open
