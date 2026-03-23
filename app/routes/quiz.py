from flask import Blueprint, jsonify, render_template, request

from app import db, get_roadmap
from app.models import QuizResult
from app.routes.main import login_required, record_activity

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/parcours/<parcours_id>/module/<module_id>/quiz/<int:niveau>")
@login_required
def quiz_view(parcours_id, module_id, niveau):
    roadmap = get_roadmap()
    parcours = next((p for p in roadmap["parcours"] if p["id"] == parcours_id), None)
    if not parcours:
        return "Parcours non trouvé", 404

    module = None
    for etape in parcours["etapes"]:
        for mod in etape["modules"]:
            if mod["id"] == module_id:
                module = mod
                break

    if not module:
        return "Module non trouvé", 404

    contenu = module.get("contenu", {}).get(f"niveau_{niveau}", {})
    questions = contenu.get("quiz", [])

    total_xp = sum(p.xp_earned for p in __import__("app.models", fromlist=["UserProgress"]).UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "quiz.html",
        parcours=parcours,
        module=module,
        niveau=niveau,
        questions=questions,
        total_xp=total_xp,
        level=level,
    )


@quiz_bp.route(
    "/api/parcours/<parcours_id>/module/<module_id>/quiz/<int:niveau>/submit",
    methods=["POST"],
)
@login_required
def submit_quiz(parcours_id, module_id, niveau):
    data = request.get_json()
    score = data.get("score", 0)
    total = data.get("total", 0)
    passed = score >= total * 0.7

    quiz_id = f"{parcours_id}/{module_id}/niveau_{niveau}"
    result = QuizResult(quiz_id=quiz_id, score=score, total=total, passed=passed)
    db.session.add(result)
    db.session.commit()

    xp = score * 20 if passed else 0
    if xp > 0:
        record_activity(xp)

    return jsonify({"success": True, "passed": passed, "xp": xp})
