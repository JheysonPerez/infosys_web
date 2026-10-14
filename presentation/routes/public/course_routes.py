from flask import Blueprint, render_template, session, request
from application.services.course_service import CourseService
from application.services.statistic_service import StatisticService
from collections import defaultdict

course_bp = Blueprint("courses", __name__)


def generate_duration_ranges(courses):
    durations = []

    for c in courses:
        try:
            duration = int(c.get("duration_weeks", 0))

            if duration:
                durations.append(duration)

        except:
            pass

    ranges = []

    if durations:

        min_duration = min(durations)
        max_duration = max(durations)

        step = 4

        start = (min_duration // step) * step

        if start <= 0:
            start = 1

        while start <= max_duration:
            end = start + step - 1
            ranges.append((start, end))
            start += step

    return ranges


@course_bp.route("/courses")
def list_courses():

    is_admin = session.get("is_admin", False)

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "")
    modality = request.args.get("modality", "")
    level = request.args.get("level", "")
    duration = request.args.get("duration", "")

    # 1. Obtener los cursos FILTRADOS según la búsqueda del usuario
    courses = CourseService.filter_courses(
        search=search,
        category=category,
        modality=modality,
        level=level,
        duration=duration,
        include_inactive=is_admin,
    )

    # 2. Limpieza de espacios en 'category' para evitar duplicados en los títulos
    for course in courses:
        if isinstance(course, dict):
            raw_cat = course.get("category")
            course["category"] = raw_cat.strip() if raw_cat else "Sin categoría"

    # 3. Agrupar los cursos filtrados por categoría
    courses_by_category = defaultdict(list)
    for course in courses:
        cat_name = course.get("category", "Sin categoría")
        courses_by_category[cat_name].append(course)

    # 4. Obtener TODOS los cursos para extraer la lista completa del selector de categorías
    all_courses = CourseService.filter_courses(include_inactive=is_admin)

    categorias = sorted(
        list(
            {
                (c.get("category") or "Sin categoría").strip()
                for c in all_courses
                if isinstance(c, dict) and c.get("category")
            }
        )
    )

    duration_ranges = CourseService.get_duration_ranges(all_courses)

    return render_template(
        "courses/list.html",
        courses=courses,
        courses_by_category=dict(courses_by_category),
        is_admin=is_admin,
        categorias=categorias,
        modalidades=CourseService.get_modalities(),
        niveles=CourseService.get_levels(),
        duration_ranges=duration_ranges,
    )


@course_bp.route("/courses/<int:course_id>")
def course_detail(course_id):

    course = CourseService.get_moodle_course(course_id)

    if not course:
        return ("Curso no encontrado", 404)

    if not session.get("is_admin", False) and not course.get("visible", True):

        return ("Curso no disponible", 403)

    StatisticService.register_event("course_view", course_id)

    return render_template("courses/detail.html", course=course)