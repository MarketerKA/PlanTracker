import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email Settings
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "youremail@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "your-app-password")
MAIL_FROM = os.getenv("MAIL_FROM", "youremail@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "PlanTracker App")

# Frontend URL for redirections
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Email verification settings
VERIFICATION_URL_BASE = os.getenv("VERIFICATION_URL_BASE", "http://localhost:8000") 