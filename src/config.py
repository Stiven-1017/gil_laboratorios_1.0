import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('APP_SECRET_KEY', 'dev-key-change-me')
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_USER = os.getenv('DB_USER', 'gil_user')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'gil_password_2025')
    MYSQL_DB = os.getenv('DB_NAME', 'gil_laboratorios')
    MYSQL_CURSORCLASS = 'DictCursor'