from flask import Blueprint, render_template

from app import get_roadmap
from app.models import UserProgress
from app.routes.main import login_required

roadmap_bp = Blueprint("roadmap", __name__)


def get_parcours_progress(parcours_id, etapes):
    total_modules = sum(len(e["modules"]) for e in etapes)
    if total_modules == 0:
        return 0
    completed = UserProgress.query.filter_by(
        parcours_id=parcours_id, completed=True
    ).count()
    return int(completed / total_modules * 100)


@roadmap_bp.route("/roadmap")
@login_required
def roadmap_view():
    roadmap = get_roadmap()
    parcours_list = []
    certifications = []

    for p in roadmap["parcours"]:
        pct = get_parcours_progress(p["id"], p["etapes"])
        entry = {**p, "progress": pct}
        if p["id"].startswith("cert-"):
            certifications.append(entry)
        else:
            parcours_list.append(entry)

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "roadmap.html",
        parcours=parcours_list,
        certifications=certifications,
        total_xp=total_xp,
        level=level,
    )


@roadmap_bp.route("/parcours/<parcours_id>")
@login_required
def parcours_view(parcours_id):
    roadmap = get_roadmap()
    parcours = next((p for p in roadmap["parcours"] if p["id"] == parcours_id), None)
    if not parcours:
        return "Parcours non trouvé", 404

    progress_records = UserProgress.query.filter_by(parcours_id=parcours_id).all()
    progress_map = {pr.module_id: pr for pr in progress_records}

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    etapes_data = []
    prev_etape_pct = 100  # First etape is always unlocked

    for etape in parcours["etapes"]:
        unlocked = prev_etape_pct >= 50
        modules_data = []
        completed_in_etape = 0

        for mod in etape["modules"]:
            pr = progress_map.get(mod["id"])
            mod_data = {
                **mod,
                "xp_earned": pr.xp_earned if pr else 0,
                "xp_total": mod["niveaux"] * mod["xp_par_niveau"],
                "niveau_actuel": pr.niveau if pr else 0,
                "completed": pr.completed if pr else False,
                "unlocked": unlocked,
            }
            if pr and pr.completed:
                completed_in_etape += 1
            modules_data.append(mod_data)

        total_in_etape = len(etape["modules"])
        etape_pct = int(completed_in_etape / total_in_etape * 100) if total_in_etape > 0 else 0
        prev_etape_pct = etape_pct

        etapes_data.append({
            "id": etape["id"],
            "titre": etape.get("titre", ""),
            "titre_en": etape.get("titre_en", etape.get("titre", "")),
            "modules": modules_data,
            "progress": etape_pct,
            "unlocked": unlocked,
        })

    global_pct = get_parcours_progress(parcours_id, parcours["etapes"])

    return render_template(
        "parcours.html",
        parcours=parcours,
        etapes=etapes_data,
        global_pct=global_pct,
        total_xp=total_xp,
        level=level,
    )


@roadmap_bp.route("/parcours/<parcours_id>/module/<module_id>")
@login_required
def module_view(parcours_id, module_id):
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

    pr = UserProgress.query.filter_by(
        parcours_id=parcours_id, module_id=module_id
    ).first()

    niveau_actuel = pr.niveau if pr else 0
    xp_earned = pr.xp_earned if pr else 0

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    niveaux_data = []
    for i in range(1, module["niveaux"] + 1):
        unlocked = i <= niveau_actuel + 1
        completed = i <= niveau_actuel
        contenu = module.get("contenu", {}).get(f"niveau_{i}", {})
        niveaux_data.append({
            "numero": i,
            "unlocked": unlocked,
            "completed": completed,
            "has_cours": bool(contenu.get("cours")),
            "has_quiz": bool(contenu.get("quiz")),
            "has_flashcards": bool(contenu.get("flashcards")),
            "has_lab": bool(contenu.get("lab")),
        })

    return render_template(
        "module.html",
        parcours=parcours,
        module=module,
        niveaux=niveaux_data,
        niveau_actuel=niveau_actuel,
        xp_earned=xp_earned,
        total_xp=total_xp,
        level=level,
    )
