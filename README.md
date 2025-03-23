# Real-Time Chat Application

## Overview

This is a real-time multi-user chat application built using Python FastAPI and MySQL for the assessment purpose. The application allows users to register, log in, join chat rooms, and exchange messages in real-time using WebSockets.

## Demo

[Watch the Demo Video on YouTube](https://youtu.be/WQMTb10nnHI)

## Features

- User authentication (register, login, logout)
- Real-time messaging with WebSockets
- Multiple chat rooms
- User online status tracking
- Message history persistence
- Dockerized deployment with separate containers for app and database
- Database backup and restore functionality

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: MySQL 8.0
- **Real-time Communication**: WebSockets
- **API Documentation**: Swagger UI (OpenAPI)
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT (JSON Web Tokens)

## Project Structure

```
.
├── backend/                  # Main application code
│   ├── app/                  # FastAPI application
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality (config, security)
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── main.py           # Application entry point
│   ├── alembic/              # Database migrations
│   ├── Dockerfile            # Docker configuration for the app
│   ├── docker-requirements.txt # Python dependencies
│   └── websocket_test.html   # HTML client for testing WebSockets
├── postman_collections/      # Postman collection for API testing
├── docker-compose.yml        # Docker Compose configuration
├── DOCKER_SETUP.md           # Docker setup instructions
├── WEBSOCKET_TESTING.md      # WebSocket testing guide
└── .env                      # Environment variables
```

## API Endpoints

| Method | Endpoint                      | Description                             |
| ------ | ----------------------------- | --------------------------------------- |
| POST   | /api/register                 | Register a new user                     |
| POST   | /api/login                    | Log in and get JWT token                |
| POST   | /api/logout                   | Log out user                            |
| GET    | /api/chat/rooms               | List all chat rooms                     |
| GET    | /api/chat/rooms/{id}          | Get specific chat room details          |
| POST   | /api/chat/rooms/{id}/messages | Send a message to a chat room           |
| GET    | /api/chat/rooms/{id}/messages | Get message history for a chat room     |
| WS     | /ws/{room_id}                 | WebSocket connection for real-time chat |

## Running the Application

### Using Docker (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/ENGRZULQARNAIN/real_time_chat_application_with_fastapi_and_mysql.git
   cd real_time_chat_application
   ```

2. Start the application with Docker Compose:

   ```bash
   docker-compose up -d
   ```

3. Access the application:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

Refer to [DOCKER_SETUP.md](DOCKER_SETUP.md) for more detailed Docker instructions.

### Manual Setup (Development)

1. Install dependencies:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r docker-requirements.txt
   ```

2. Set up the MySQL database:

   ```bash
   # Run MySQL (you can use Docker for this)
   docker run --name mysql_chat -e MYSQL_ROOT_PASSWORD=your_password -e MYSQL_DATABASE=real_time_chat_db -p 3306:3306 -d mysql:8.0
   ```

3. Update the `.env` file with your database configuration

4. Run database migrations:

   ```bash
   cd backend
   alembic upgrade head
   ```

5. Start the application:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Testing the APIs

### Postman Collection

A Postman collection is provided in the `postman_collections` folder. Import this collection into Postman to test the REST API endpoints.

### WebSocket Testing

For testing the WebSocket functionality, refer to [WEBSOCKET_TESTING.md](WEBSOCKET_TESTING.md) or use the HTML test client at `backend/websocket_test.html`.

## Database Backup & Restore

### Backup MySQL Database

```bash
# Inside the running Docker container
docker exec -it real_time_chat_application_db_1 mysqldump -u root -p real_time_chat_db > backup.sql

# Or from the host machine
docker exec real_time_chat_application_db_1 mysqldump -u root -pyour_password real_time_chat_db > backup.sql
```

### Restore MySQL Database

```bash
# To restore from a backup file
docker exec -i real_time_chat_application_db_1 mysql -u root -pyour_password real_time_chat_db < backup.sql
```

## Security Considerations

- The JWT secret key should be changed for production environments
- Database passwords should be more secure in production
- Consider implementing rate limiting for the API
- Implement proper data validation and sanitization

## License

This project is licensed under the terms of the license included in the repository.
