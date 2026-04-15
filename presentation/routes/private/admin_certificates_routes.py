from flask import Blueprint, render_template, request, redirect, url_for, send_file
from infrastructure.database.postgres import db
from domain.models.certificate import Certificate
from domain.models.course import Course
from application.services.certificate_service import (
    create_certificate,
    generate_certificate_image,
)

from io import BytesIO
from datetime import datetime
import qrcode
from PIL import Image

admin_cert_bp = Blueprint(
    "admin_certificates",
    __name__,
    url_prefix="/admin/certificates"
)

# BUSCAR
@admin_cert_bp.route("/search", methods=["GET"])
def search_admin():
    code = request.args.get("code", "").strip()
    dni = request.args.get("dni", "").strip()
    results = []

    if code and not dni:
        results = Certificate.query.filter(Certificate.code.ilike(f"%{code}%")).all()
    elif dni and not code:
        results = Certificate.query.filter(Certificate.student_dni == dni).all()
    elif code and dni:
        results = Certificate.query.filter(
            Certificate.code.ilike(f"%{code}%"),
            Certificate.student_dni == dni
        ).all()

    return render_template("certificates/search.html", results=results, is_admin=True)

# CREAR
@admin_cert_bp.route("/new", methods=["GET", "POST"])
def new_certificate():
    courses = Course.query.all()

    if request.method == "POST":
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        cert_type = request.form.get("type", "generated")
        file = request.files.get("certificate_file")

        create_certificate(
            request.form["student_name"].strip(),
            request.form["student_dni"].strip(),
            int(request.form["course_id"]),
            request.form["code"].strip().upper(),
            start_date,
            end_date,
            type=cert_type,
            file=file
        )

        return redirect(url_for("admin_certificates.search_admin"))

    return render_template("admin/certificates/form.html", courses=courses, cert=None)

# EDITAR 
@admin_cert_bp.route("/edit/<int:cert_id>", methods=["GET", "POST"])
def edit_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    courses = Course.query.all()

    if request.method == "POST":
        cert.student_name = request.form["student_name"].strip()
        cert.student_dni = request.form["student_dni"].strip()
        cert.course_id = int(request.form["course_id"])
        cert.code = request.form["code"].strip().upper()
        cert.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        cert.end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

        cert.type = request.form.get("type", cert.type)

        file = request.files.get("certificate_file")

        if cert.type == "external" and file and file.filename:
            create_certificate(
                cert.student_name,
                cert.student_dni,
                cert.course_id,
                cert.code,
                cert.start_date,
                cert.end_date,
                type="external",
                file=file
            )

        course = Course.query.get(cert.course_id)
        cert.course_name = course.title
        cert.duration = course.estimated_hours

        db.session.commit()

        return redirect(url_for("admin_certificates.search_admin"))

    return render_template("admin/certificates/form.html", cert=cert, courses=courses)

# ELIMINAR
@admin_cert_bp.route("/delete/<int:cert_id>", methods=["POST"])
def delete_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    db.session.delete(cert)
    db.session.commit()
    return redirect(url_for("admin_certificates.search_admin"))

# PREVIEW
@admin_cert_bp.route("/preview", methods=["POST"])
def preview_certificate():
    student_name = request.form.get("student_name", "").strip()
    course_id = request.form.get("course_id")
    code = request.form.get("code", "").strip() or "PREVIEW123"
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    cert_type = request.form.get("type", "generated")

    if not student_name or not course_id or not start_date or not end_date:
        return "", 204

    course = Course.query.get(course_id)
    if not course:
        return "", 204

    # GENERATED
    if cert_type == "generated":
        temp_cert = Certificate(
            student_name=student_name,
            code=code,
            course_name=course.title,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            duration=course.estimated_hours,
            course=course,
            syllabus_snapshot=course.syllabus,
            template_snapshot=course.certificate_image
        )

        image = generate_certificate_image(temp_cert)

    # EXTERNAL 
    else:
        file = request.files.get("certificate_file")
        if not file or not file.filename:
            return "", 204

        image = Image.open(file).convert("RGB")

        qr_url = f"https://infosys-web.onrender.com/certificados?code={code}"

        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(qr_url)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((90, 90))

        image.paste(qr_img, (image.width - 730, image.height - 137))

    img_io = BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")