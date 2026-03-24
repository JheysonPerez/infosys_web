from flask import Blueprint, render_template, session
from datetime import date

from infosys_web.domain.models.services import Service
from infosys_web.domain.models.news import News
from infosys_web.domain.models.course import Course
from infosys_web.application.services.statistic_service import StatisticService

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

    # noticias activas no expiradas
    news = News.query.filter(
        (News.expires_at == None) | 
        (News.expires_at >= date.today())
    ).order_by(
        News.published_at.desc()
    ).limit(3).all()

    return render_template(
        "home/index.html",
        services=services,
        courses=courses,
        news=news,
        is_admin=session.get("is_admin", False)
    )