# backend/run_backend.py
import uvicorn
import os
import sys

if __name__ == "__main__":
    # Calculate the project root directory (one level up from 'backend' directory)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Add the project root to sys.path
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    
    print(f"PROJECT_ROOT added to sys.path: {PROJECT_ROOT}")
    print(f"Current sys.path: {sys.path}") # For debugging

    # Now Uvicorn should be able to find 'backend.app.main'
    # and within 'backend.app.main', imports should resolve correctly
    # if they are absolute from the project root (e.g., from backend.app.schemas)

    uvicorn.run(
        "backend.app.main:app",  # Path to the FastAPI app instance from project root
        host="0.0.0.0",
        port=8000,
        reload=True,
        # reload_dirs=[os.path.join(PROJECT_ROOT, "backend")], # Optional: specify reload dirs
    )