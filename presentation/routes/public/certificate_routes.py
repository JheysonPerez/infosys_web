from flask import Blueprint, render_template, request, session
from domain.models.certificate import Certificate

cert_bp = Blueprint("certificates", __name__)

@cert_bp.route("/certificados", methods=["GET"])
def search():
    code = request.args.get("code", "").strip()
    dni = request.args.get("dni", "").strip()

    results = []

    if code and not dni:
        results = Certificate.query.filter(
            Certificate.code == code
        ).all()

    elif dni and not code:
        results = Certificate.query.filter(
            Certificate.student_dni == dni
        ).all()

    elif code and dni:
        results = Certificate.query.filter(
            Certificate.code == code,
            Certificate.student_dni == dni
        ).all()

    is_admin = session.get("user") and session.get("user").get("is_admin")

    return render_template(
        "certificates/search.html",
        results=results,
        is_admin=is_admin
    )