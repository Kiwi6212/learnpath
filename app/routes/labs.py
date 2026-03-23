from flask import Blueprint, jsonify, render_template, request

from app import db, get_roadmap
from app.models import LabResult, UserProgress
from app.routes.main import login_required, record_activity

labs_bp = Blueprint("labs", __name__)


@labs_bp.route("/parcours/<parcours_id>/module/<module_id>/lab/<int:niveau>")
@login_required
def lab_view(parcours_id, module_id, niveau):
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
    lab = contenu.get("lab", {})

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "lab.html",
        parcours=parcours,
        module=module,
        niveau=niveau,
        lab=lab,
        total_xp=total_xp,
        level=level,
    )


@labs_bp.route(
    "/api/parcours/<parcours_id>/module/<module_id>/lab/<int:niveau>/complete",
    methods=["POST"],
)
@login_required
def complete_lab(parcours_id, module_id, niveau):
    lab_id = f"{parcours_id}/{module_id}/niveau_{niveau}"

    existing = LabResult.query.filter_by(lab_id=lab_id, completed=True).first()
    if not existing:
        result = LabResult(lab_id=lab_id, completed=True)
        db.session.add(result)
        db.session.commit()
        record_activity(50)

    return jsonify({"success": True, "xp": 50})
