# Docker Development Setup

This project uses Docker Compose to run both frontend (Next.js) and backend (FastAPI with SPL Generation) services with Python 3.12.10.

## Prerequisites

- Docker Desktop
- Docker Compose
- Git

## Quick Start

### Windows
```cmd
# Start development environment
docker-dev.bat dev

# Start in background
docker-dev.bat dev-daemon

# View logs
docker-dev.bat logs

# Stop services
docker-dev.bat stop
```

### Linux/macOS
```bash
# Make script executable
chmod +x docker-dev.sh

# Start development environment
./docker-dev.sh dev

# Start in background
./docker-dev.sh dev-daemon

# View logs
./docker-dev.sh logs

# Stop services
./docker-dev.sh stop
```

## Services

- **Frontend**: Next.js app running on http://localhost:3000
- **Backend**: FastAPI with SPL Generation on http://localhost:8000

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
GROQ_API_KEY=your_groq_api_key_here
FRONTEND_ORIGIN=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
ENVIRONMENT=development
DEBUG=true
```

## Docker Commands

### Development Mode
```bash
# Build and start services
docker-compose -f docker-compose.dev.yml up --build

# Start in background
docker-compose -f docker-compose.dev.yml up --build -d

# Stop services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Shell into backend
docker-compose -f docker-compose.dev.yml exec backend bash

# Shell into frontend
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### Production Mode
```bash
# Build and start services
docker-compose up --build

# Start in background
docker-compose up --build -d
```

## API Endpoints

### Backend API
- Health Check: http://localhost:8000/api/health
- API Documentation: http://localhost:8000/docs
- SPL Generation: http://localhost:8000/api/spl/generate-spl
- Relevance Check: http://localhost:8000/api/spl/check-relevance
- Service Status: http://localhost:8000/api/spl/service-status

### Frontend
- Main App: http://localhost:3000

## Development Features

- **Hot Reload**: Both frontend and backend support hot reloading
- **Volume Mounting**: Source code changes are reflected immediately
- **Health Checks**: Services have health check endpoints
- **Logging**: Centralized logging with Docker Compose
- **Python 3.12.10**: Backend uses the latest Python version

## Troubleshooting

### Backend Issues
```bash
# Check backend logs
docker-compose -f docker-compose.dev.yml logs backend

# Shell into backend for debugging
docker-compose -f docker-compose.dev.yml exec backend bash
```

### Frontend Issues
```bash
# Check frontend logs
docker-compose -f docker-compose.dev.yml logs frontend

# Shell into frontend
docker-compose -f docker-compose.dev.yml exec frontend sh
```

### Clean Reset
```bash
# Windows
docker-dev.bat clean

# Linux/macOS
./docker-dev.sh clean
```

## File Structure
```
├── docker/
│   ├── backend.Dockerfile      # Backend Docker configuration
│   └── frontend.Dockerfile     # Frontend Docker configuration
├── apps/
│   ├── backend/               # FastAPI application
│   │   ├── app/
│   │   ├── data/              # SPL data files
│   │   └── requirements.txt
│   └── frontend/              # Next.js application
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development configuration
├── .env                       # Environment variables
├── docker-dev.sh             # Linux/macOS helper script
├── docker-dev.bat            # Windows helper script
└── README.docker.md          # This file
```

## SPL Generation Features

The backend includes a sophisticated SPL (Splunk Processing Language) generation system:

- **RAG Integration**: Uses Retrieval Augmented Generation with Splunk documentation
- **Company Context Selection**: Intelligent company/index selection based on query context
- **Syntax Validation**: Validates generated SPL queries
- **Relevance Detection**: Determines if queries are Splunk-related
- **Multi-method Analysis**: Combines LLM, semantic, and keyword-based analysis

## Testing

```bash
# Test backend API
curl http://localhost:8000/api/health

# Test SPL generation
curl -X POST http://localhost:8000/api/spl/generate-spl \
  -H "Content-Type: application/json" \
  -d '{"query": "Show failed login attempts in the last 24 hours", "verbose": false}'
```
