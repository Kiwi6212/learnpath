from flask import Blueprint, jsonify, render_template, request

from app import db, get_roadmap
from app.models import ExamResult, UserProgress
from app.routes.main import login_required, record_activity

exams_bp = Blueprint("exams", __name__)


@exams_bp.route("/exams")
@login_required
def exams_list():
    roadmap = get_roadmap()
    certifications = [p for p in roadmap["parcours"] if p["id"].startswith("cert-")]
    exam_results = ExamResult.query.order_by(ExamResult.completed_at.desc()).all()

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "exam.html",
        certifications=certifications,
        exam_results=exam_results,
        total_xp=total_xp,
        level=level,
        mode="list",
    )


@exams_bp.route("/exams/<exam_id>/start")
@login_required
def start_exam(exam_id):
    roadmap = get_roadmap()
    cert = next(
        (p for p in roadmap["parcours"] if p["id"] == exam_id), None
    )
    if not cert:
        return "Examen non trouvé", 404

    exam_config = cert.get("exam", {})
    questions = exam_config.get("questions", [])
    duration = exam_config.get("duration_min", 60)
    passing_score = exam_config.get("passing_score", 80)

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "exam.html",
        cert=cert,
        questions=questions,
        duration=duration,
        passing_score=passing_score,
        total_xp=total_xp,
        level=level,
        mode="exam",
    )


@exams_bp.route("/api/exams/<exam_id>/submit", methods=["POST"])
@login_required
def submit_exam(exam_id):
    data = request.get_json()
    score = data.get("score", 0)
    total = data.get("total", 0)
    duration_sec = data.get("duration_sec", 0)
    passing_score = data.get("passing_score", 80)

    pct = int(score / total * 100) if total > 0 else 0
    passed = pct >= passing_score

    result = ExamResult(
        exam_id=exam_id,
        score=score,
        total=total,
        duration_sec=duration_sec,
        passed=passed,
    )
    db.session.add(result)
    db.session.commit()

    xp = 200 if passed else 50
    record_activity(xp)

    return jsonify({
        "success": True,
        "passed": passed,
        "pct": pct,
        "xp": xp,
    })
