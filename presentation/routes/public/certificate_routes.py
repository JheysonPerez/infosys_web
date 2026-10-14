from flask import Blueprint, render_template, request, session
from domain.models.certificate import Certificate

cert_bp = Blueprint("certificates", __name__)


@cert_bp.route("/certificados", methods=["GET"])
def search():
    code = request.args.get("code", "").strip()
    dni = request.args.get("dni", "").strip()

    results = []

    if code and not dni:
        results = Certificate.query.filter_by(
            code=code
        ).all()

    elif dni and not code:
        results = Certificate.query.filter_by(
            student_dni=dni
        ).all()

    elif code and dni:
        results = Certificate.query.filter_by(
            code=code,
            student_dni=dni
        ).all()

    # Preparar datos para la vista
    certificates = []

    for cert in results:

        certificates.append({
            "id": cert.id,
            "student_name": cert.student_name,
            "student_dni": cert.student_dni,
            "code": cert.code,
            "course_name": cert.course_name,
            "start_date": cert.start_date,
            "end_date": cert.end_date,
            "issue_date": cert.issue_date,
            "certificate_image": cert.certificate_image
        })

    is_admin = (
        session.get("user")
        and session.get("user").get("is_admin")
    )

    return render_template("certificates/search.html", results=certificates, is_admin=is_admin)