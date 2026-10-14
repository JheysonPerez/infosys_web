from flask import (Blueprint, render_template, redirect, url_for, flash, request, current_app,)
from werkzeug.utils import secure_filename
from collections import defaultdict
import os
from datetime import datetime

from presentation.routes.private.admin_guard import admin_required
from application.services.course_service import CourseService

admin_courses_bp = Blueprint("admin_courses", __name__, url_prefix="/admin/courses")


@admin_courses_bp.route("/")
@admin_required
def list_courses():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "")
    modality = request.args.get("modality", "")
    level = request.args.get("level", "")
    duration = request.args.get("duration", "")

    # 1. Cursos FILTRADOS según la búsqueda actual
    courses = CourseService.filter_courses(
        search=search,
        category=category,
        modality=modality,
        level=level,
        duration=duration,
        include_inactive=True,
    )

    # 2. Limpieza de espacios en 'category' para evitar duplicados en la lista filtrada
    for course in courses:
        if isinstance(course, dict):
            raw_cat = course.get("category")
            course["category"] = raw_cat.strip() if raw_cat else "Sin categoría"

    # 3. Agrupar los cursos filtrados por categoría
    courses_by_category = defaultdict(list)
    for course in courses:
        cat_name = course.get("category", "Sin categoría")
        courses_by_category[cat_name].append(course)

    # 4. Obtener TODOS los cursos para poblar el selector/dropdown de categorías
    all_courses = CourseService.filter_courses(include_inactive=True)

    categorias = sorted(
        list(
            {
                (c.get("category") or "Sin categoría").strip()
                for c in all_courses
                if isinstance(c, dict) and c.get("category")
            }
        )
    )

    return render_template(
        "courses/list.html",
        courses=courses,
        courses_by_category=dict(courses_by_category),
        is_admin=True,
        categorias=categorias,
        modalidades=CourseService.get_modalities(),
        niveles=CourseService.get_levels(),
        duration_ranges=CourseService.get_duration_ranges(all_courses),
    )


def save_image(file, folder):
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_name = f"{timestamp}_{filename}"

        upload_folder = os.path.join(
            current_app.root_path, "static", "images", folder
        )

        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, unique_name)
        file.save(filepath)

        return f"images/{folder}/{unique_name}"

    return None


def delete_file(folder, filename):
    if filename:
        name_only = os.path.basename(filename)
        path = os.path.join(
            current_app.root_path, "static", "images", folder, name_only
        )
        if os.path.exists(path):
            os.remove(path)


@admin_courses_bp.route("/edit/<int:course_id>", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    course = CourseService.get_moodle_course(course_id)

    if not course:
        flash("Curso no encontrado", "danger")
        return redirect(url_for("admin_courses.list_courses"))

    if request.method == "POST":
        data = request.form.to_dict()
        data["featured"] = request.form.get("featured") == "1"

        cert_file = request.files.get("certificate_image")

        if cert_file and cert_file.filename:
            new_cert_path = save_image(cert_file, "certificates")

            if new_cert_path:
                old_cert = course.get("certificate_image")

                if old_cert:
                    delete_file("certificates", old_cert)

                data["certificate_image"] = new_cert_path

        CourseService.update(course_id, data)

        flash("Curso actualizado correctamente", "success")
        return redirect(url_for("admin_courses.list_courses"))

    moodle_courses = CourseService.get_moodle_courses()

    categorias = sorted(
        {
            c.get("category").strip()
            for c in moodle_courses
            if isinstance(c, dict) and c.get("category")
        }
    )

    return render_template(
        "admin/courses/form.html",
        course=course,
        moodle_courses=moodle_courses,
        categorias=categorias,
        is_admin=True,
    )