# Real-Time Chat Application

A real-time multi-user chat application built with FastAPI and MySQL that enables seamless user interaction through websockets. The application provides a robust platform for users to communicate in real-time within different chat rooms.

## Features

- User authentication (register, login, logout)
- Real-time messaging using WebSocket
- Multiple chat rooms support
- Message history persistence
- Dockerized application setup
- MySQL database integration

## API Endpoints

### Authentication

- `POST /api/register` - Create a new user account
- `POST /api/login` - User login
- `POST /api/logout` - User logout

### Chat Rooms

- `GET /api/chat/rooms` - List all available chat rooms
- `GET /api/chat/rooms/{id}` - Get specific chat room details
- `POST /api/chat/rooms/{id}/messages` - Send message to a chat room
- `GET /api/chat/rooms/{id}/messages` - Get chat room message history

## Data Models

### Chat Room

- `id`: Unique identifier
- `name`: Room name
- `users`: List of active users

### Message

- `id`: Unique identifier
- `text`: Message content
- `sender_id`: User ID of sender
- `room_id`: Chat room ID
- `created_at`: Message timestamp

## Docker Setup

The application uses Docker Compose to run two containers:

1. FastAPI application
2. MySQL database

### Running with Docker

```bash
docker-compose up --build
```
