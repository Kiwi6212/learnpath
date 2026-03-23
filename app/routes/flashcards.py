from flask import Blueprint, jsonify, render_template, request

from app import db, get_roadmap
from app.models import FlashcardReview, UserProgress
from app.routes.main import login_required, record_activity

flashcards_bp = Blueprint("flashcards", __name__)


@flashcards_bp.route(
    "/parcours/<parcours_id>/module/<module_id>/flashcards/<int:niveau>"
)
@login_required
def flashcards_view(parcours_id, module_id, niveau):
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
    cards = contenu.get("flashcards", [])

    total_xp = sum(p.xp_earned for p in UserProgress.query.all())
    level = total_xp // 500 + 1

    return render_template(
        "flashcards.html",
        parcours=parcours,
        module=module,
        niveau=niveau,
        cards=cards,
        total_xp=total_xp,
        level=level,
    )


@flashcards_bp.route(
    "/api/flashcards/review",
    methods=["POST"],
)
@login_required
def review_card():
    data = request.get_json()
    card_id = data.get("card_id", "")
    known = data.get("known", False)

    review = FlashcardReview(card_id=card_id, known=known)
    db.session.add(review)
    db.session.commit()

    xp = 10 if known else 5
    record_activity(xp)

    return jsonify({"success": True, "xp": xp})
