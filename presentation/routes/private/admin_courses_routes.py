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

# LISTAR CURSOS
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

# GUARDAR IMAGEN
def save_image(file):
    if file and file.filename != "":
        filename = secure_filename(file.filename)

        # nombre único
        unique_name = f"{uuid.uuid4().hex}_{filename}"

        # ruta REAL del proyecto
        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "images",
            "courses"
        )

        # crear carpeta si no existe
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, unique_name)

        # guardar archivo
        file.save(filepath)

        print("GUARDADO EN:", filepath)  # debug opcional

        return unique_name

    return None

# CREAR CURSO
@admin_courses_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_course():

    if request.method == "POST":
        data = request.form.to_dict()

        # imagen
        image_file = request.files.get("image")
        image_name = save_image(image_file)

        if image_name:
            data["image"] = image_name

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

        # nueva imagen
        image_file = request.files.get("image")
        image_name = save_image(image_file)

        # SOLO actualizar si suben nueva imagen
        if image_name:
            data["image"] = image_name

        CourseService.update(course_id, data)

        flash("Curso actualizado correctamente", "success")
        return redirect(url_for("admin_courses.list_courses"))

    return render_template("admin/courses/form.html", course=course)

# ELIMINAR CURSO
@admin_courses_bp.route("/delete/<int:course_id>", methods=["POST"])
@admin_required
def delete_course(course_id):

    CourseService.delete(course_id)

    flash("Curso eliminado correctamente", "success")
    return redirect(url_for("admin_courses.list_courses"))