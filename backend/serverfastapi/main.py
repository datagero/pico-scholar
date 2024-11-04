# Add serverfastapi to the path to avoid import errors
import sys
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager
# from dotenv import load_dotenv
# load_dotenv()  # This will load the variables from the .env file

# Set up paths and imports
from serverfastapi.core.config import settings
# from api.project_management.routes import router as project_router
# from api.document_management.routes import router as document_router
from serverfastapi.api.semantic_search.routes import router as search_router
# from api.translation.routes import router as translation_router
# from api.rag_system.routes import router as rag_router
from serverfastapi.app_init import initialize_services
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services and configurations during the app lifespan."""
    # Load all services (databases, indexes, etc.) and assign to the app's state
    services = initialize_services()
    app.state.services = services

    # Create all database tables
    from serverfastapi.core.db import Base
    Base.metadata.create_all(bind=services["engine"])

    yield  # The app is now running and serving requests

# Initialize the FastAPI app with middleware and routers
app = FastAPI(
    title="Backend API",
    description="Backend services for document and project management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
# app.include_router(project_router, prefix="/projects", tags=["Projects"])
# app.include_router(document_router, prefix="/documents", tags=["Documents"])
app.include_router(search_router, prefix="/search", tags=["Search"])
# app.include_router(translation_router, prefix="/translate", tags=["Translation"])
# app.include_router(rag_router, prefix="/rag", tags=["RAG"])

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logging.info("Starting up the FastAPI app...")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down the FastAPI app...")

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "Healthy"}

# Main entry point for running the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(settings.PORT),
        reload=True,
        loop="asyncio",
    )