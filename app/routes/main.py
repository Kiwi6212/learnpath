from datetime import date, datetime, timezone
from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for

from app import db, get_roadmap
from app.models import DailyActivity, ExamResult, UserProgress

main_bp = Blueprint("main", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        token = current_app.config.get("LP_TOKEN", "")
        if token and not session.get("authenticated"):
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return decorated


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    from flask import current_app
    error = None
    if request.method == "POST":
        token = request.form.get("token", "")
        if token == current_app.config.get("LP_TOKEN", ""):
            session["authenticated"] = True
            return redirect(url_for("main.home"))
        error = "Token invalide"
    return render_template("login.html", error=error)


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main_bp.route("/")
@login_required
def home():
    return redirect(url_for("roadmap.roadmap_view"))


@main_bp.route("/stats")
@login_required
def stats():
    roadmap = get_roadmap()
    progress_records = UserProgress.query.all()
    exam_results = ExamResult.query.order_by(ExamResult.completed_at.desc()).all()

    total_xp = sum(p.xp_earned for p in progress_records)
    level = total_xp // 500 + 1

    parcours_stats = []
    for p in roadmap["parcours"]:
        total_modules = sum(len(e["modules"]) for e in p["etapes"])
        completed = sum(
            1 for pr in progress_records
            if pr.parcours_id == p["id"] and pr.completed
        )
        pct = int(completed / total_modules * 100) if total_modules > 0 else 0
        parcours_stats.append({
            "id": p["id"],
            "titre": p["titre"],
            "titre_en": p.get("titre_en", p["titre"]),
            "icon": p.get("icon", ""),
            "couleur": p.get("couleur", "#4A90D9"),
            "completed": completed,
            "total": total_modules,
            "pct": pct,
        })

    # Streak calculation
    activities = DailyActivity.query.order_by(DailyActivity.date.desc()).all()
    streak = 0
    today = date.today()
    for i, a in enumerate(activities):
        expected = today if i == 0 else activities[i - 1].date
        from datetime import timedelta
        if i > 0:
            expected = activities[i - 1].date - timedelta(days=1)
        if a.date == expected or (i == 0 and (today - a.date).days <= 1):
            streak += 1
        else:
            break

    return render_template(
        "stats.html",
        total_xp=total_xp,
        level=level,
        parcours_stats=parcours_stats,
        exam_results=exam_results,
        streak=streak,
        total_completed=sum(1 for p in progress_records if p.completed),
        total_modules=sum(
            len(e["modules"]) for pa in roadmap["parcours"] for e in pa["etapes"]
        ),
    )


def record_activity(xp):
    today = date.today()
    activity = DailyActivity.query.filter_by(date=today).first()
    if activity:
        activity.xp_earned += xp
    else:
        activity = DailyActivity(date=today, xp_earned=xp)
        db.session.add(activity)
    db.session.commit()
