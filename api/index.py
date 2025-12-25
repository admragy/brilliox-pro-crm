"""
Vercel API Entry Point for Brilliox Pro CRM
This file acts as the bridge between Vercel's serverless environment and the FastAPI application.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app
from app.main import app

# Export the app object for Vercel's Python runtime
handler = app
