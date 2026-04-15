from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
import os
import uuid

from presentation.routes.private.admin_guard import admin_required
from application.services.course_service import CourseService
from presentation.routes.public.course_routes import generate_duration_ranges

admin_courses_bp = Blueprint(
    "admin_courses",
    __name__,
    url_prefix="/admin/courses"
)

@admin_courses_bp.route("/")
@admin_required
def list_courses():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "")
    modality = request.args.get("modality", "")
    level = request.args.get("level", "")
    duration = request.args.get("duration", "")

    courses = CourseService.filter_courses(
        search=search,
        category=category,
        modality=modality,
        level=level,
        duration=duration,
        include_inactive=True
    )

    all_courses = CourseService.get_all()
    duration_ranges = generate_duration_ranges(all_courses)

    return render_template(
        "courses/list.html",
        courses=courses,
        is_admin=True,
        duration_ranges=duration_ranges
    )

# GUARDAR IMAGEN (ahora retorna ruta relativa completa)
def save_image(file, folder):
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "images",
            folder
        )
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, unique_name)
        file.save(filepath)

        # Retornar ruta relativa completa
        return f"images/{folder}/{unique_name}"
    return None

# ELIMINAR IMAGEN 
def delete_file(folder, filename):
    if filename:
        # Extraer solo el nombre del archivo si viene con ruta relativa
        name_only = os.path.basename(filename)
        path = os.path.join(
            current_app.root_path,
            "static",
            "images",
            folder,
            name_only
        )
        if os.path.exists(path):
            os.remove(path)

# CREAR CURSO
@admin_courses_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_course():
    if request.method == "POST":
        data = request.form.to_dict()

        image_file = request.files.get("image")
        image_path = save_image(image_file, "courses")
        if image_path:
            data["image"] = image_path

        cert_file = request.files.get("certificate_image")
        cert_path = save_image(cert_file, "certificates")
        if cert_path:
            data["certificate_image"] = cert_path

        CourseService.create(data)
        flash("Curso creado correctamente", "success")
        return redirect(url_for("admin_courses.list_courses"))

    return render_template("admin/courses/form.html", course=None)

# EDITAR CURSO
@admin_courses_bp.route("/edit/<int:course_id>", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    course = CourseService.get_by_id(course_id)

    if not course:
        flash("Curso no encontrado", "danger")
        return redirect(url_for("admin_courses.list_courses"))

    if request.method == "POST":
        data = request.form.to_dict()

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            new_image_path = save_image(image_file, "courses")
            if new_image_path:
                delete_file("courses", course.image)
                data["image"] = new_image_path

        cert_file = request.files.get("certificate_image")
        if cert_file and cert_file.filename:
            new_cert_path = save_image(cert_file, "certificates")
            if new_cert_path:
                delete_file("certificates", course.certificate_image)
                data["certificate_image"] = new_cert_path

        CourseService.update(course_id, data)
        flash("Curso actualizado correctamente", "success")
        return redirect(url_for("admin_courses.list_courses"))

    return render_template("admin/courses/form.html", course=course)

# ELIMINAR CURSO
@admin_courses_bp.route("/delete/<int:course_id>", methods=["POST"])
@admin_required
def delete_course(course_id):
    course = CourseService.get_by_id(course_id)

    if course:
        delete_file("courses", course.image)
        delete_file("certificates", course.certificate_image)

    CourseService.delete(course_id)
    flash("Curso eliminado correctamente", "success")
    return redirect(url_for("admin_courses.list_courses"))