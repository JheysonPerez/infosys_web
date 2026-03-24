from flask import Blueprint, render_template, session, request
from application.services.course_service import CourseService
from application.services.statistic_service import StatisticService

course_bp = Blueprint("courses", __name__)

# Función para generar rangos de duración dinámicos
def generate_duration_ranges(courses):
    durations = []

    for c in courses:
        if c.duration_weeks:
            try:
                durations.append(int(c.duration_weeks))
            except:
                pass

    duration_ranges = []

    if durations:
        min_duration = min(durations)
        max_duration = max(durations)

        step = 4
        start = (min_duration // step) * step

        if start <= 0:
            start = 1

        while start <= max_duration:
            end = start + step - 1
            duration_ranges.append((start, end))
            start += step

    return duration_ranges


# LISTAR CURSOS
@course_bp.route("/courses")
def list_courses():

    is_admin = session.get("is_admin", False)

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
        include_inactive=is_admin
    )

    all_courses = CourseService.get_all() if is_admin else CourseService.get_active()
    duration_ranges = generate_duration_ranges(all_courses)

    return render_template(
        "courses/list.html",
        courses=courses,
        is_admin=is_admin,
        duration_ranges=duration_ranges
    )

# DETALLE CURSO 
@course_bp.route("/courses/<int:course_id>")
def course_detail(course_id):

    course = CourseService.get_by_id(course_id)

    if not course:
        return "Curso no encontrado", 404

    if not session.get("is_admin", False) and course.status != "activo":
        return "Curso no disponible", 403

    # REGISTRAR VISTA DEL CURSO
    StatisticService.register_event("course_view", course_id)

    return render_template(
        "courses/detail.html",
        course=course
    )