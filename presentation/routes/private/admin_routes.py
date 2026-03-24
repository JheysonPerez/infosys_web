from flask import Blueprint, render_template, request, jsonify
from presentation.routes.private.admin_guard import admin_required
from application.services.statistic_service import StatisticService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html")


@admin_bp.route("/stats")
@admin_required
def stats():
    # Visitas
    visits_mode         = request.args.get("visits_mode", "range")
    visits_single_date  = request.args.get("visits_single_date")
    visits_month        = request.args.get("visits_month")
    visits_start_date   = request.args.get("visits_start_date")
    visits_end_date     = request.args.get("visits_end_date")

    # Cursos
    courses_mode        = request.args.get("courses_mode", "range")
    courses_order       = request.args.get("courses_order", "desc")
    courses_single_date = request.args.get("courses_single_date")
    courses_month       = request.args.get("courses_month")
    courses_start_date  = request.args.get("courses_start_date")
    courses_end_date    = request.args.get("courses_end_date")

    # Servicios
    services_mode       = request.args.get("services_mode", "range")
    services_order      = request.args.get("services_order", "desc")
    services_single_date = request.args.get("services_single_date")
    services_month      = request.args.get("services_month")
    services_start_date = request.args.get("services_start_date")
    services_end_date   = request.args.get("services_end_date")

    # Obtener los datos
    visits_data = StatisticService.visits(
        mode=visits_mode,
        single_date=visits_single_date,
        month=visits_month,
        start_date=visits_start_date,
        end_date=visits_end_date
    )

    courses_data = StatisticService.courses_stats(
        order=courses_order,
        mode=courses_mode,
        single_date=courses_single_date,
        month=courses_month,
        start_date=courses_start_date,
        end_date=courses_end_date
    )

    services_data = StatisticService.services_stats(
        order=services_order,
        mode=services_mode,
        single_date=services_single_date,
        month=services_month,
        start_date=services_start_date,
        end_date=services_end_date
    )

    # Respuesta según tipo de petición

    # Si es una petición AJAX 
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "visits": visits_data,
            "top_courses": courses_data,
            "top_services": services_data,
        })

    # Respuesta normal 
    return render_template(
        "admin/stats.html",

        # Datos para los gráficos
        visits=visits_data,
        top_courses=courses_data,
        top_services=services_data,

        # Parámetros para mantener el estado de los formularios
        visits_mode=visits_mode,
        visits_single_date=visits_single_date,
        visits_month=visits_month,
        visits_start_date=visits_start_date,
        visits_end_date=visits_end_date,

        courses_mode=courses_mode,
        courses_order=courses_order,
        courses_single_date=courses_single_date,
        courses_month=courses_month,
        courses_start_date=courses_start_date,
        courses_end_date=courses_end_date,

        services_mode=services_mode,
        services_order=services_order,
        services_single_date=services_single_date,
        services_month=services_month,
        services_start_date=services_start_date,
        services_end_date=services_end_date
    )