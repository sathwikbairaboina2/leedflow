from fastapi import FastAPI
from celery import Celery
from app.api import endpoints
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(title="Leedflow Names Predictor", version="1.0.0")

# Include API routers
app.include_router(endpoints.router, prefix="/api/v1", tags=["names"])


@app.get("/")
async def root():
    return {"message": "Welcome to the leedflow names predictor!"}
