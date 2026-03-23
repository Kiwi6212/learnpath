from datetime import datetime, timezone

from app import db


class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parcours_id = db.Column(db.String(100), nullable=False)
    module_id = db.Column(db.String(100), nullable=False)
    niveau = db.Column(db.Integer, default=1)
    xp_earned = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<UserProgress {self.parcours_id}/{self.module_id}>"


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class FlashcardReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(200), nullable=False)
    known = db.Column(db.Boolean, default=False)
    reviewed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    duration_sec = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class LabResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class DailyActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    xp_earned = db.Column(db.Integer, default=0)
