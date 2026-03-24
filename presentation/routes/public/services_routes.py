from flask import Blueprint, render_template, session, request
from application.services.service_service import ServiceService
from application.services.statistic_service import StatisticService

services_bp = Blueprint("services", __name__, url_prefix="/services")

# RUTA SERVICIOS
@services_bp.route("/")
def services_page():

    is_admin = session.get("is_admin", False)

    search = request.args.get("search", "").strip()
    service_type = request.args.get("service_type", "")
    modality = request.args.get("modality", "")
    duration = request.args.get("duration", "")

    services = ServiceService.filter_services(
        search=search,
        service_type=service_type,
        modality=modality,
        duration=duration,
        include_inactive=is_admin
    )

    service_types = ServiceService.get_service_types()
    modalities = ServiceService.get_modalities()
    duration_ranges = ServiceService.get_duration_ranges(services)

    return render_template(
        "services/list.html",
        services=services,
        is_admin=is_admin,
        service_types=service_types,
        modalities=modalities,
        duration_ranges=duration_ranges
    )


# DETALLE SERVICIO 
@services_bp.route("/<int:service_id>")
def service_detail(service_id):

    service = ServiceService.get_by_id(service_id)

    if not service:
        return "Servicio no encontrado", 404

    if not session.get("is_admin", False) and service.status != 'activo':
        return "Servicio no disponible", 403

    # REGISTRAR VISTA
    StatisticService.register_event("service_view", service_id)

    return render_template("services/detail.html", service=service)