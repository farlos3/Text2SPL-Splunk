from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import chat, health, spl

# Create FastAPI instance
app = FastAPI(
    title="Chat Backend API",
    description="FastAPI backend for chat application",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(spl.router, prefix="/api/spl", tags=["spl"])

@app.get("/")
async def root():
    return {"message": "Chat Backend API is running!"}
