import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    LP_TOKEN = os.getenv("LP_TOKEN", "")
    SQLALCHEMY_DATABASE_URI = "sqlite:///learnpath.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "app", "static", "data")
