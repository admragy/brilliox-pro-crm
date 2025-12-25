"""
Brilliox Pro CRM - Main Entry Point
v7.0.0 - Unified System Architecture

This file serves as the entry point for the application.
It imports and runs the FastAPI application from app.main
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Run the main application
    from app.main import app
    import uvicorn

    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
else:
    # Import app for production servers
    from app.main import app
