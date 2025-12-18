# AI Interviewer - Backend

FastAPI backend service for the AI-powered technical interview practice system.

## Tech Stack

- **Framework**: FastAPI 0.108.0
- **Python**: 3.12.7
- **Database**: PostgreSQL with SQLAlchemy 2.0.23
- **Authentication**: JWT with python-jose
- **Testing**: pytest, pytest-asyncio, httpx

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality (config, security, etc.)
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic layer
│   └── utils/            # Utility functions
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Python 3.12.7 or higher
- pip (Python package manager)
- PostgreSQL database (for future database integration)

### Installation

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Server

**Development mode with auto-reload:**

```bash
uvicorn app.main:app --reload --port 8000
```

**Production mode:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

### Running Tests

**Run all tests:**

```bash
pytest
```

**Run with coverage:**

```bash
pytest --cov=app tests/
```

**Run specific test file:**

```bash
pytest tests/test_main.py
```

## API Endpoints

### Health Check

- `GET /` - Root endpoint with API information
- `GET /api/v1/health` - Health check endpoint

## Environment Variables

See [.env.example](.env.example) for all available environment variables.

Key variables:

- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `ENVIRONMENT` - Application environment (development/production)

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions and classes

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest fixtures for common test setup

## License

This project is part of a diploma project.
