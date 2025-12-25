"""
Vercel API Entry Point for Brilliox Pro CRM
This file acts as the bridge between Vercel's serverless environment and the FastAPI application.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the FastAPI app
from app.main import app

# For Vercel's Python runtime, we need to export the app as 'app'
app = app
