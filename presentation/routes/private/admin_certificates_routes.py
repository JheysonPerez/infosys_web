from flask import (Blueprint, render_template, request, redirect, url_for, send_file, current_app)
from infrastructure.database.postgres import db
from domain.models.certificate import Certificate
from domain.models.course import Course
from application.services.course_service import CourseService
from application.services.certificate_service import create_certificate, generate_certificate_image
from io import BytesIO
from datetime import datetime
import qrcode
from PIL import Image, ImageFont, ImageDraw
import os
import uuid

admin_cert_bp = Blueprint("admin_certificates", __name__, url_prefix="/admin/certificates")


def get_code_font():
    try:
        font_path = os.path.join(
            current_app.root_path, "static", "fonts", "DejaVuSans-Bold.ttf"
        )
        return ImageFont.truetype(font_path, 12)
    except:
        return ImageFont.load_default()


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
            Certificate.student_dni == dni,
        ).all()
    return render_template("certificates/search.html", results=results, is_admin=True)


# CREAR
@admin_cert_bp.route("/new", methods=["GET", "POST"])
def new_certificate():
    courses = CourseService.get_moodle_courses()
    if request.method == "POST":
        start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        issue_date = datetime.strptime(request.form["issue_date"], "%Y-%m-%d")
        cert_type = request.form.get("type", "generated")
        file = request.files.get("certificate_file")

        create_certificate(
            student_name=request.form["student_name"].strip(),
            student_dni=request.form["student_dni"].strip(),
            course_id=int(request.form["course_id"]),
            code=request.form["code"].strip().upper(),
            start_date=start_date,
            end_date=end_date,
            issue_date=issue_date,
            type=cert_type,
            file=file,
        )
        return redirect(url_for("admin_certificates.search_admin"))
    return render_template("admin/certificates/form.html", courses=courses, cert=None)


# EDITAR
@admin_cert_bp.route("/edit/<int:cert_id>", methods=["GET", "POST"])
def edit_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    courses = CourseService.get_moodle_courses()

    if request.method == "POST":
        cert.student_name = request.form["student_name"].strip()
        cert.student_dni = request.form["student_dni"].strip()
        cert.course_id = int(request.form["course_id"])
        cert.code = request.form["code"].strip().upper()
        cert.start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
        cert.end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
        cert.issue_date = datetime.strptime(request.form["issue_date"], "%Y-%m-%d")
        cert.type = request.form.get("type", cert.type)

        # Actualizar datos del curso
        course = Course.query.get(cert.course_id)
        if course:
            moodle_course = CourseService.get_moodle_course(course.moodle_course_id)
            if moodle_course:
                cert.course_name = moodle_course.get("fullname", course.title)
                cert.duration = moodle_course.get("estimated_hours")
                cert.syllabus_snapshot = moodle_course.get("syllabus")
                cert.template_snapshot = moodle_course.get("certificate_image")

        file = request.files.get("certificate_file")

        if cert.type == "external" and file and file.filename:
            upload_folder = os.path.join(current_app.root_path, "static", "images", "external_certificates")
            os.makedirs(upload_folder, exist_ok=True)
            filename = f"{uuid.uuid4().hex}_{file.filename}"
            path = os.path.join(upload_folder, filename)

            image = Image.open(file).convert("RGB")
            draw = ImageDraw.Draw(image)

            # QR
            qr_url = f"https://infosys-web.onrender.com/certificado/{cert.code}"
            qr = qrcode.make(qr_url).resize((90, 90))
            image.paste(qr, (image.width - 140, image.height - 127))

            # Código - MISMA FUENTE Y TAMAÑO
            font = get_code_font()
            bbox = draw.textbbox((0, 0), cert.code, font=font)
            text_width = bbox[2] - bbox[0]

            x_codigo = 100 + 800 - text_width + 19
            y_codigo = image.height - 105

            draw.text((x_codigo, y_codigo), cert.code, fill="black", font=font)

            image.save(path, quality=95)
            cert.certificate_image = f"images/external_certificates/{filename}"

        elif cert.type == "generated":
            output_folder = os.path.join(current_app.root_path, "static", "images", "generated_certificates")
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, f"{cert.code}.png")
            image = generate_certificate_image(cert)
            image.save(output_path)
            cert.certificate_image = f"images/generated_certificates/{cert.code}.png"

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
    issue_date = request.form.get("issue_date")
    cert_type = request.form.get("type", "generated")

    if not all([student_name, course_id, start_date, end_date, issue_date]):
        return "", 204

    moodle_course = CourseService.get_moodle_course(int(course_id))
    if not moodle_course:
        return "", 204

    course = Course.query.filter_by(moodle_course_id=int(course_id)).first()
    course_name = moodle_course.get("fullname", "Curso")

    if cert_type == "generated":
        temp_cert = Certificate(
            student_name=student_name,
            code=code,
            course_name=course_name,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            issue_date=datetime.strptime(issue_date, "%Y-%m-%d"),
            duration=moodle_course.get("estimated_hours"),
            course=course,
            syllabus_snapshot=moodle_course.get("syllabus"),
            template_snapshot=moodle_course.get("certificate_image"),
        )
        image = generate_certificate_image(temp_cert)

    else:  # EXTERNAL
        file = request.files.get("certificate_file")
        if not file or not file.filename:
            return "", 204

        image = Image.open(file).convert("RGB")
        draw = ImageDraw.Draw(image)

        # QR
        qr_url = f"https://infosys-web.onrender.com/certificado/{code}"
        qr = qrcode.make(qr_url).resize((90, 90))
        qr_x = image.width - 140
        qr_y = image.height - 127
        image.paste(qr, (qr_x, qr_y))

        font = get_code_font()   
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]

        x_base = 100
        body_width = 800
        x_codigo = x_base + body_width - text_width + 19
        y_codigo = image.height - 23   

        draw.text((x_codigo, y_codigo), code, fill="black", font=font)

    img_io = BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")