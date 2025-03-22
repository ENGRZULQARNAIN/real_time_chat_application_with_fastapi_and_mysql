# Docker Setup for Real-Time Chat Application

This document explains how to use Docker to run the Real-Time Chat Application with a separate container for the MySQL database.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Project Structure

The application consists of two Docker containers:

1. **app** - FastAPI backend application
2. **db** - MySQL database

## Running the Application

### 1. Start the containers

```bash
docker-compose up -d
```

This command will:

- Build the application image from the Dockerfile
- Pull the MySQL image from Docker Hub
- Start both containers
- Link them together

### 2. Stop the containers

```bash
docker-compose down
```

### 3. View logs

```bash
docker-compose logs -f
```

### 4. Database Persistence

The MySQL data is stored in a named volume `mysql_data`, so your data will persist even if you stop or remove the containers.

## Configuration

The database connection settings are configured in the docker-compose.yml file. If you need to modify these settings (like changing passwords), update them in:

1. `docker-compose.yml` - For the Docker environment
2. `.env` - For local development

## Accessing the Application

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Troubleshooting

If you encounter any issues with the MySQL connection, try:

```bash
docker-compose down -v  # This will remove volumes, including the database data
docker-compose up -d    # Start fresh
```

Note: This will delete all data in the database.

## Security Notes

- For production environments, change the default MySQL password in the docker-compose.yml file
- Consider using Docker secrets for sensitive information in production
