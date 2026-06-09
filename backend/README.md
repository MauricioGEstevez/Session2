# FastAPI JWT Authentication Backend

A Python FastAPI backend with JWT (JSON Web Token) authentication implementation.

## Overview

This application provides:
- **Login Endpoint**: Accepts username and password, returns JWT access token and refresh token
- **Token Refresh Endpoint**: Accepts refresh token and returns a new access token
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`
- **Token Expiration**: Access tokens expire after 300 seconds (5 minutes)
- **Refresh Token Expiration**: Refresh tokens expire after 7 days

## Features

- JWT-based authentication
- Access token with 300-second expiration
- Refresh token mechanism for obtaining new access tokens
- Password hashing with bcrypt
- Docker and Docker Compose support
- Poetry for dependency management
- Automated health checks
- API documentation with Swagger UI and ReDoc

## Prerequisites

- Python 3.11+
- Poetry (for local development)
- Docker and Docker Compose (for containerized deployment)
- curl or a REST client (for testing endpoints)

## Installation & Setup

### Option 1: Local Development with Poetry

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Create `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```
   
   You can customize the values in `.env` if needed for your environment.

5. **Run the application**:
   ```bash
   poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at `http://localhost:8000`

### Option 2: Docker Deployment

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

   The API will be available at `http://localhost:8000`

3. **Stop the container**:
   ```bash
   docker-compose down
   ```

## API Endpoints

### 1. Health Check
- **Endpoint**: `GET /health`
- **Description**: Check if the service is running
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "jwt-auth-backend"
  }
  ```

### 2. Root Endpoint
- **Endpoint**: `GET /`
- **Description**: Get API information
- **Response**:
  ```json
  {
    "service": "JWT Authentication Backend",
    "version": "0.1.0",
    "endpoints": {
      "login": "/login (POST)",
      "refresh": "/refresh (POST)",
      "health": "/health (GET)",
      "docs": "/docs (Swagger UI)",
      "redoc": "/redoc (ReDoc)"
    }
  }
  ```

### 3. Login
- **Endpoint**: `POST /login`
- **Description**: Login with credentials to get JWT tokens
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **Response** (HTTP 200):
  ```json
  {
    "access_token": "******",
    "refresh_token": "******",
    "token_type": "bearer",
    "expires_in": 300
  }
  ```
- **Error Response** (HTTP 401):
  ```json
  {
    "detail": "Incorrect username or password"
  }
  ```

### 4. Refresh Token
- **Endpoint**: `POST /refresh`
- **Description**: Refresh the access token
- **Request Body**:
  ```json
  {
    "refresh_token": "******"
  }
  ```
- **Response** (HTTP 200):
  ```json
  {
    "access_token": "******",
    "refresh_token": "******",
    "token_type": "bearer",
    "expires_in": 300
  }
  ```
- **Error Response** (HTTP 401):
  ```json
  {
    "detail": "Invalid refresh token"
  }
  ```

## Usage Examples

### Using curl

1. **Login to get tokens**:
   ```bash
   curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Save the access token**:
   ```bash
   export ACCESS_TOKEN=$(curl -s -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}' | jq -r '.access_token')
   ```

3. **Use the access token** (example with protected endpoint):
   ```bash
   curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: *** "
   ```

4. **Refresh the token**:
   ```bash
   curl -X POST "http://localhost:8000/refresh" \
     -H "Content-Type: application/json" \
     -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
   ```

### Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Login
login_response = requests.post(
    f"{BASE_URL}/login",
    json={"username": "admin", "password": "admin123"}
)
tokens = login_response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")

# Refresh token
refresh_response = requests.post(
    f"{BASE_URL}/refresh",
    json={"refresh_token": refresh_token}
)
new_tokens = refresh_response.json()
new_access_token = new_tokens["access_token"]

print(f"New Access Token: {new_access_token}")
```

## API Documentation

The API automatically generates interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Visit these URLs in your browser to explore and test the API interactively.

## Project Structure

```
backend/
├── main.py                 # Main FastAPI application
├── pyproject.toml         # Poetry configuration and dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose orchestration
├── .env                   # Environment variables (example)
└── README.md              # This file
```

## Environment Variables

- `SECRET_KEY`: Secret key for JWT signing (change in production)
- `DEBUG`: Debug mode (set to False in production)

## Security Recommendations

1. **Change the Secret Key**: In production, set a strong `SECRET_KEY` in the `.env` file
2. **Use HTTPS**: Always use HTTPS in production
3. **Secure Credentials**: Never hardcode credentials in the application
4. **Token Rotation**: Implement token rotation mechanism
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks
6. **CORS**: Configure CORS appropriately for your frontend

## Development

### Running Tests (if implemented)

```bash
poetry run pytest
```

### Code Quality

To maintain code quality, you can use:

```bash
# Lint with flake8
poetry run flake8 main.py

# Format with black
poetry run black main.py
```

## Troubleshooting

### Port 8000 already in use

If port 8000 is already in use, you can change the port in the startup command:

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8001
```

Or in `docker-compose.yml`, change the port mapping:

```yaml
ports:
  - "8001:8000"
```

### Token Expired

Access tokens expire after 300 seconds. If you get an "Invalid token" error, use the refresh endpoint to get a new access token.

### Docker build fails

Make sure you have:
- Docker installed and running
- Sufficient disk space
- No conflicting containers running on port 8000

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please refer to the FastAPI documentation:
- FastAPI: https://fastapi.tiangolo.com/
- Python-Jose: https://github.com/mpdavis/python-jose
- Passlib: https://passlib.readthedocs.io/
