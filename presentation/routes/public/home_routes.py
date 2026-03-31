from flask import Blueprint, render_template, session
from datetime import date

from domain.models.services import Service
from domain.models.news import News
from domain.models.course import Course
from application.services.statistic_service import StatisticService

home_bp = Blueprint("home", __name__)

# RUTA HOME
@home_bp.route("/")
def index():

    # Registrar visita
    StatisticService.register_event("visit")

    # servicios destacados activos
    services = Service.query.filter_by(
        featured=True,
        status="activo"
    ).all()

    # cursos destacados activos
    courses = Course.query.filter_by(
        featured=True,
        status="activo"
    ).all()

    # solo cursos que tienen certificado
    certificates = Course.query.filter(
        Course.featured == True,
        Course.status == "activo",
        Course.certificate_image != None
    ).all()

    # noticias activas no expiradas
    news = News.query.filter(
        (News.expires_at == None) |
        (News.expires_at >= date.today())
    ).order_by(
        News.published_at.desc()
    ).limit(3).all()

    # noticias destacadas para el modal
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