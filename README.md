# Social Analysis

This is a FastAPI-based backend for a media platform. It provides functionalities for admin authentication, media uploads, secure streaming links, and view logging.

## Project Structure

```
.env
├───app.db
├───main.py
├───__pycache__/
├───uploads/
├───venv/
├───config.py
├───database.py
├───lifespan.py
├───models.py
├───schemas.py
├───security.py
├───routers/
│   ├───__init__.py
│   ├───auth.py
│   ├───media.py
│   └───root.py
└───README.md
```

- **main.py**: The main entry point of the application.
- **app.py**: Creates and configures the FastAPI app.
- **config.py**: Application configuration.
- **database.py**: Database connection and session management.
- **lifespan.py**: Lifespan events for the FastAPI application.
- **models.py**: SQLAlchemy ORM models.
- **schemas.py**: Pydantic models for data validation and serialization.
- **security.py**: Security-related functions (hashing, tokens, auth).
- **routers/**: Directory containing the API routers.
  - **auth.py**: Authentication routes.
  - **media.py**: Media-related routes.
  - **root.py**: Root route.
- **uploads/**: Directory where uploaded media files are stored.
- **app.db**: SQLite database file.

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following environment variables:
   ```
   SECRET_KEY="your-secret-key"
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

## Usage

Run the application using uvicorn:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Endpoints

- **GET /**: Root endpoint, returns `{"status": "ok"}`.
- **POST /auth/signup**: Admin user signup.
- **POST /auth/login**: Admin user login.
- **POST /media**: Upload a new media file.
- **GET /media/{media_id}/stream-url**: Get a secure, time-limited streaming URL for a media file.
- **GET /stream**: Stream a media file using a secure URL.
