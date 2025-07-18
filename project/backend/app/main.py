# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import api as api_v1 # Import the v1 api router
from .db.database import create_db_tables # Import the function to create tables
from .core.config import settings # To access settings if needed

# Call this function to create tables when the app starts
# In a real app, you might run this once manually or use migrations.
# For this project, creating them on startup if they don't exist is fine.
def create_tables_on_startup():
    print("Attempting to create database tables...")
    try:
        create_db_tables()
        print("Database tables checked/created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Depending on the error, you might want to exit or handle it differently
        # For example, if the DB is not reachable, the app won't work anyway.

app = FastAPI(title="Gemini Chatbot API")

# --- Middleware ---
# CORS (Cross-Origin Resource Sharing)
# Allows requests from your Streamlit frontend (which will run on a different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:8501"] for Streamlit dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Event Handlers ---
@app.on_event("startup")
async def startup_event():
    print("FastAPI application startup...")
    create_tables_on_startup()
    # You could also initialize other resources here, e.g., ML models if not done per-request

# --- Routers ---
app.include_router(api_v1.api_router, prefix="/api/v1") # Include v1 of the API

# --- Basic Root Endpoint ---
@app.get("/")
async def root():
    return {"message": "Welcome to the Gemini Chatbot API!"}