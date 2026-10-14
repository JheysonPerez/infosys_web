from flask import Blueprint, render_template, session
from datetime import date

from domain.models.services import Service
from domain.models.news import News

from application.services.course_service import CourseService
from application.services.statistic_service import StatisticService

home_bp = Blueprint("home", __name__)


# RUTA HOME
@home_bp.route("/")
def index():

    # Registrar visita
    StatisticService.register_event("visit")

    # Servicios destacados activos
    services = Service.query.filter_by(
        featured=True,
        status="activo"
    ).all()

    # Cursos obtenidos desde Moodle + datos locales
    all_courses = CourseService.get_moodle_courses()

    # Cursos destacados activos
    courses = [
        course
        for course in all_courses
        if course.get("featured")
        and course.get("status") == "activo"
    ]

    # Cursos destacados que tienen certificado
    certificates = [
        course
        for course in all_courses
        if course.get("featured")
        and course.get("status") == "activo"
        and course.get("certificate_image")
    ]

    # Noticias activas no expiradas
    news = News.query.filter(
        (News.expires_at == None) |
        (News.expires_at >= date.today())
    ).order_by(
        News.published_at.desc()
    ).limit(3).all()

    # Noticias destacadas para el modal
    featured_news = News.query.filter(
        News.featured == True,
        (News.expires_at == None) |
        (News.expires_at >= date.today())
    ).order_by(
        News.published_at.desc()
    ).all()

    return render_template(
        "home/index.html",
        services=services,
        courses=courses,
        certificates=certificates,
        news=news,
        featured_news=featured_news,
        is_admin=session.get("is_admin", False)
    )