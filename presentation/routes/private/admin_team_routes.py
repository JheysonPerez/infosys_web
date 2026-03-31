from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from presentation.routes.private.admin_guard import admin_required
from application.services.team_service import TeamService

admin_team_bp = Blueprint("admin_team", __name__, url_prefix="/admin/team")
UPLOAD_FOLDER = "static/images/team"

def save_image(file):
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return filename
    return None

@admin_team_bp.route("/")
@admin_required
def list_team():
    team = TeamService.get_all()
    for member in team:
        member.socials = TeamService.build_social_links(member)
    return render_template(
        "about/about.html",
        team=team,
        is_admin=True
    )

@admin_team_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_member():
    if request.method == "POST":
        data = request.form.to_dict()
        image_file = request.files.get("image")
        filename = save_image(image_file)
        if filename:
            data["image"] = filename
        TeamService.create(data)
        flash("Miembro creado correctamente", "success")
        return redirect(url_for("admin_team.list_team"))
    return render_template("admin/team/form.html", member=None)

@admin_team_bp.route("/edit/<int:member_id>", methods=["GET", "POST"])
@admin_required
def edit_member(member_id):
    member = TeamService.get_by_id(member_id)
    if request.method == "POST":
        data = request.form.to_dict()
        image_file = request.files.get("image")
        if image_file and image_file.filename:
            if member.image:
                old_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, member.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            data["image"] = save_image(image_file)
        else:
            data["image"] = member.image
        TeamService.update(member_id, data)
        flash("Miembro actualizado correctamente", "success")
        return redirect(url_for("admin_team.list_team"))
    return render_template("admin/team/form.html", member=member)

@admin_team_bp.route("/delete/<int:member_id>", methods=["POST"])
@admin_required
def delete_member(member_id):
    member = TeamService.get_by_id(member_id)
    if member and member.image:
        image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, member.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    TeamService.delete(member_id)
    flash("Miembro eliminado", "success")
    return redirect(url_for("admin_team.list_team"))