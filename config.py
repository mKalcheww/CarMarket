import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-2025')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///carmarket.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'cars')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024