from flask import Blueprint, render_template, request, redirect, url_for
from infrastructure.database.postgres import db
from domain.models.certificate import Certificate
from domain.models.course import Course
from application.services.certificate_service import create_certificate

import os

admin_cert_bp = Blueprint(
    "admin_certificates",
    __name__,
    url_prefix="/admin/certificates"
)

@admin_cert_bp.route("/search", methods=["GET"])
def search_admin():
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

    for cert in results:
        if not cert.certificate_image and cert.course and cert.course.certificate_image:
            cert.certificate_image = os.path.basename(cert.course.certificate_image)

    return render_template(
        "certificates/search.html",
        results=results,
        is_admin=True
    )

@admin_cert_bp.route("/new", methods=["GET", "POST"])
def new_certificate():
    courses = Course.query.all()

    if request.method == "POST":
        name = request.form["student_name"]
        dni = request.form["student_dni"]
        course_id = request.form["course_id"]

        create_certificate(name, dni, course_id)

        return redirect(url_for("admin_certificates.search_admin"))

    return render_template(
        "admin/certificates/form.html",
        courses=courses,
        cert=None
    )

@admin_cert_bp.route("/edit/<int:cert_id>", methods=["GET", "POST"])
def edit_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    courses = Course.query.all()

    if request.method == "POST":
        cert.student_name = request.form["student_name"]
        cert.student_dni = request.form["student_dni"]
        cert.course_id = request.form["course_id"]

        course = Course.query.get(cert.course_id)
        if course and course.certificate_image:
            cert.certificate_image = os.path.basename(course.certificate_image)

        db.session.commit()
        return redirect(url_for("admin_certificates.search_admin"))

    return render_template(
        "admin/certificates/form.html",
        cert=cert,
        courses=courses
    )

@admin_cert_bp.route("/delete/<int:cert_id>", methods=["POST"])
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)

    db.session.delete(cert)
    db.session.commit()

    return redirect(url_for("admin_certificates.search_admin"))