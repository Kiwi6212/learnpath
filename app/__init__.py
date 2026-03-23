import json
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()

_roadmap_cache = None


def get_roadmap():
    global _roadmap_cache
    if _roadmap_cache is None:
        data_path = os.path.join(Config.DATA_DIR, "roadmap.json")
        with open(data_path, "r", encoding="utf-8") as f:
            _roadmap_cache = json.load(f)
    return _roadmap_cache


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.roadmap import roadmap_bp
    from app.routes.courses import courses_bp
    from app.routes.quiz import quiz_bp
    from app.routes.flashcards import flashcards_bp
    from app.routes.labs import labs_bp
    from app.routes.exams import exams_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(labs_bp)
    app.register_blueprint(exams_bp)

    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
