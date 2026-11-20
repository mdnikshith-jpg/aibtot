import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OCR_API_KEYS = os.getenv("OCR_API_KEYS", "").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretchangeit")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
BOT_API_KEY = os.getenv("BOT_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./storage.db")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")

# Google OAuth Credentials (for future use)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# ... existing code ...
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")