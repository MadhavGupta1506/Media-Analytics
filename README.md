# Media Platform API

A FastAPI-based media platform API that allows users to upload, stream, and manage media assets (videos and audio). The API includes authentication, media upload, streaming with secure URLs, analytics for media views, and Redis-based caching and rate limiting.

## Features

- **Authentication**: User signup and login with JWT tokens
- **Media Upload**: Upload video and audio files
- **Secure Streaming**: Generate secure stream URLs for media access
- **Analytics**: Track media views with IP logging and daily statistics
- **Async Database**: Uses SQLAlchemy with async support and SQLite for development
- **Redis Caching**: Redis integration for improved performance and rate limiting
- **Admin Users**: Role-based access for media management
- **Rate Limiting**: Built-in rate limiting to prevent abuse

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration and session management
│   ├── models.py            # SQLAlchemy models (AdminUser, MediaAsset, MediaViewLog)
│   ├── schemas.py           # Pydantic schemas for request/response validation
│   ├── security.py          # Authentication and JWT utilities
│   ├── redis_client.py      # Redis client configuration and connection
│   ├── routers/
│   │   ├── auth.py          # Authentication endpoints (signup, login)
│   │   └── media.py         # Media management endpoints
│   ├── utils/
│   │   ├── rate_limit.py    # Rate limiting utilities
│   │   └── cache.py         # Caching utilities
│   └── tests/
│       ├── conftest.py      # Test configuration
│       └── test_media.py    # Media endpoint tests
├── uploads/                 # Directory for uploaded media files
├── .env                     # Environment variables (created from .env.example)
├── .env.example             # Environment variables template
├── media_platform.db        # SQLite database file
├── requirements.txt         # Python dependencies
├── pytest.ini              # Pytest configuration
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker container configuration
└── README.md               # This file
```

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory.

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your configuration values (Redis URL, database URL, secret key, etc.).

## Running the Application

1. **Start the FastAPI server**:

   ```bash
   python -m app.main
   ```

   or

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation**:
   - Open your browser and go to: `http://localhost:8000/docs`
   - This will show the interactive Swagger UI for testing the API endpoints.

## API Endpoints

### Authentication

- `POST /auth/signup` - Create a new admin user account
- `POST /auth/login` - Login and receive JWT token

### Media Management

- `POST /media` - Upload a new media file (requires authentication)
- `GET /media/{media_id}/stream-url` - Generate a secure stream URL for media
- `GET /media/stream/{media_id}` - Stream media file (requires authentication)
- `POST /media/{media_id}/view` - Manually log a media view
- `GET /media/{media_id}/analytics` - Get analytics for a specific media item

## Database

The application uses SQLite for development (`media_platform.db`). On startup, the database tables are automatically created if they don't exist.

For production, you can switch to PostgreSQL by updating the `DATABASE_URL` environment variable in your `.env` file.

## Redis

The application uses Redis for caching and rate limiting. Redis connection is configured via the `REDIS_URL` environment variable.

### Running Redis Locally

You can run Redis using Docker:

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

Or use the provided Docker Compose setup:

```bash
docker-compose up redis
```

## Configuration

Environment variables are loaded from the `.env` file:

- **DATABASE_URL**: Database connection string (default: SQLite)
- **REDIS_URL**: Redis connection URL (required for Redis features)
- **SECRET_KEY**: JWT secret key for token signing
- **STREAM_TOKEN_EXPIRE_SECONDS**: Stream token expiration time (default: 600 seconds)

- **Upload Directory**: Media files are stored in the `uploads/` directory.
- **Token Expiration**: Access tokens expire after 30 minutes, stream tokens after 10 minutes (configurable).

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- Stream URLs include short-lived tokens for secure access
- Media views are logged with IP addresses for analytics

## Development

- The application uses async SQLAlchemy for database operations
- Pydantic models ensure data validation
- FastAPI provides automatic API documentation
- The project follows a modular structure with routers for different functionalities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
