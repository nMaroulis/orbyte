import uvicorn
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas, services
from backend.core import security
from backend.core.config import settings
from backend.database import SessionLocal, engine
from backend.routers import auth, gpus, tasks, payments

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Orbyte API",
    description="Decentralized GPU Rental Platform for GenAI Workloads",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware with more detailed logging
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n=== New Request ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print("Headers:", request.headers)
    
    # Log request body for non-GET requests
    if request.method not in ["GET", "HEAD"]:
        try:
            body = await request.body()
            if body:
                print("Request body:", body.decode())
        except Exception as e:
            print(f"Error reading request body: {e}")
    
    # Process the request
    response = await call_next(request)
    
    print(f"Response status: {response.status_code}")
    print("Response headers:", response.headers)
    
    # Log response body
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    if response_body:
        print("Response body:", response_body.decode())
    
    # Return a new response with the original body
    from starlette.responses import Response
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(gpus.router, prefix="/api/gpus", tags=["gpus"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "orbyte-api",
        "version": "0.1.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Orbyte API",
        "docs": "/api/docs",
        "version": "0.1.0"
    }

# Token endpoint is now handled by the auth router

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
