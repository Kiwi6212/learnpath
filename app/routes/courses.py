import markdown
from flask import Blueprint, jsonify, render_template, request

from app import db, get_roadmap
from app.models import UserProgress
from app.routes.main import login_required, record_activity

courses_bp = Blueprint("courses", __name__)


def find_module(parcours_id, module_id):
    roadmap = get_roadmap()
    parcours = next((p for p in roadmap["parcours"] if p["id"] == parcours_id), None)
    if not parcours:
        return None, None
    for etape in parcours["etapes"]:
        for mod in etape["modules"]:
            if mod["id"] == module_id:
                return parcours, mod
    return parcours, None


@courses_bp.route("/parcours/<parcours_id>/module/<module_id>/cours/<int:niveau>")
@login_required
def course_view(parcours_id, module_id, niveau):
    parcours, module = find_module(parcours_id, module_id)
    if not module:
        return "Module non trouvé", 404

    contenu = module.get("contenu", {}).get(f"niveau_{niveau}", {})
    cours_md = contenu.get("cours", "# Contenu à venir\n\nCe cours est en cours de rédaction.")
    cours_html = markdown.markdown(cours_md, extensions=["fenced_code", "tables", "nl2br"])

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "course.html",
        parcours=parcours,
        module=module,
        niveau=niveau,
        cours_html=cours_html,
        total_xp=total_xp,
        level=level,
    )


@courses_bp.route(
    "/api/parcours/<parcours_id>/module/<module_id>/cours/<int:niveau>/complete",
    methods=["POST"],
)
@login_required
def complete_course(parcours_id, module_id, niveau):
    _, module = find_module(parcours_id, module_id)
    if not module:
        return jsonify({"error": "not found"}), 404

    xp_par_niveau = module.get("xp_par_niveau", 100)
    pr = UserProgress.query.filter_by(
        parcours_id=parcours_id, module_id=module_id
    ).first()

    if not pr:
        pr = UserProgress(
            parcours_id=parcours_id,
            module_id=module_id,
            niveau=niveau,
            xp_earned=xp_par_niveau,
        )
        db.session.add(pr)
    elif niveau > pr.niveau:
        pr.niveau = niveau
        pr.xp_earned += xp_par_niveau
        if niveau >= module["niveaux"]:
            pr.completed = True
            from datetime import datetime, timezone
            pr.completed_at = datetime.now(timezone.utc)

    db.session.commit()
    record_activity(xp_par_niveau)

    return jsonify({"success": True, "xp": xp_par_niveau, "niveau": pr.niveau})
