# backend/app/core/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file from the project root
# This assumes your run_backend.py or uvicorn command is run from the project root
# or that the .env file is discoverable by python-dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
load_dotenv(dotenv_path=dotenv_path) # Load the .env file

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env" # Though load_dotenv already did the job, this is good practice
        env_file_encoding = "utf-8"
        extra = "ignore" # Ignore extra fields in .env

settings = Settings()