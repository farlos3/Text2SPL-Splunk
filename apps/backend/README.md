# FastAPI Backend

This is a FastAPI backend application for the chat system.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py          # Pydantic models for chat
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py        # Health check endpoints
│   │   └── chat.py          # Chat API endpoints
│   └── services/
│       ├── __init__.py
│       └── chat_service.py  # Business logic for chat
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables example
└── README.md               # This file
```

## Features

- **FastAPI** with automatic API documentation
- **CORS** configuration for frontend integration
- **Groq API** integration for AI chat responses
- **Pydantic** models for request/response validation
- **Modular structure** with routers, services, and models
- **Environment-based configuration**
- **Docker support** with hot-reload

## API Endpoints

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/chat` - Send chat message
- `GET /api/chat/history` - Get chat history (placeholder)

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `GROQ_API_KEY` - Your Groq API key for AI responses
- `FRONTEND_ORIGIN` - Frontend URL for CORS
- `ENVIRONMENT` - development/production
- `DEBUG` - Enable debug mode

## Running the Application

### With Docker (Recommended)
```bash
# Build and run with docker-compose
docker-compose -f docker-compose.dev.yml up backend
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once running, visit:
- http://localhost:8000/docs - Swagger UI
- http://localhost:8000/redoc - ReDoc UI
