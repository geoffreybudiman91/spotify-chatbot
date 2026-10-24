import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

# Comma-separated list of frontend origins allowed to call the API.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
