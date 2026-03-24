from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import uuid

from presentation.routes.private.admin_guard import admin_required
from application.services.service_service import ServiceService

admin_services_bp = Blueprint(
    "admin_services",
    __name__,
    url_prefix="/admin/services"
)

# carpeta de imágenes
UPLOAD_FOLDER = "static/images/services"

# guardar imagen
def save_image(file):
    if file and file.filename != "":
        filename = secure_filename(file.filename)

        # nombre único
        unique_name = f"{uuid.uuid4().hex}_{filename}"

        # crear carpeta si no existe
        full_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(full_path, exist_ok=True)

        filepath = os.path.join(full_path, unique_name)
        file.save(filepath)

        return unique_name
    return None

# LISTAR
@admin_services_bp.route("/")
@admin_required
def list_services():
    search = request.args.get("search", "").strip()
    service_type = request.args.get("service_type", "")
    modality = request.args.get("modality", "")
    duration = request.args.get("duration", "")

    services = ServiceService.filter_services(
        search=search,
        service_type=service_type,
        modality=modality,
        duration=duration,
        include_inactive=True
    )

    service_types = ServiceService.get_service_types()
    modalities = ServiceService.get_modalities()
    duration_ranges = ServiceService.get_duration_ranges(services)

    return render_template(
        "services/list.html",
        services=services,
        is_admin=True,
        service_types=service_types,
        modalities=modalities,
        duration_ranges=duration_ranges
    )

# CREAR
@admin_services_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_service():
    if request.method == "POST":
        data = request.form.to_dict()

        # imagen
        image_file = request.files.get("image")
        image_name = save_image(image_file)
        if image_name:
            data["image"] = image_name

        ServiceService.create(data)
        flash("Servicio creado correctamente", "success")
        return redirect(url_for("admin_services.list_services"))

    tipos = ServiceService.get_service_types()
    return render_template("admin/services/form.html", service=None, tipos=tipos)

# EDITAR
@admin_services_bp.route("/edit/<int:service_id>", methods=["GET", "POST"])
@admin_required
def edit_service(service_id):
    service = ServiceService.get_by_id(service_id)
    if not service:
        flash("Servicio no encontrado", "danger")
        return redirect(url_for("admin_services.list_services"))

    if request.method == "POST":
        data = request.form.to_dict()

        # imagen
        image_file = request.files.get("image")
        image_name = save_image(image_file)
        if image_name:
            data["image"] = image_name  # nueva imagen
        else:
            data["image"] = service.image  # mantiene la actual

        ServiceService.update(service_id, data)
        flash("Servicio actualizado correctamente", "success")
        return redirect(url_for("admin_services.list_services"))

    tipos = ServiceService.get_service_types()
    return render_template("admin/services/form.html", service=service, tipos=tipos)

# ELIMINAR
@admin_services_bp.route("/delete/<int:service_id>", methods=["POST"])
@admin_required
def delete_service(service_id):
    ServiceService.delete(service_id)
    flash("Servicio eliminado", "success")
    return redirect(url_for("admin_services.list_services"))