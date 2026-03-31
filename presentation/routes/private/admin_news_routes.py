from flask import Blueprint, render_template, request, redirect, url_for, flash
from presentation.routes.private.admin_guard import admin_required
from application.services.news_service import NewsService
from werkzeug.utils import secure_filename
import os
import uuid

admin_news_bp = Blueprint(
    "admin_news",
    __name__,
    url_prefix="/admin/news"
)

UPLOAD_FOLDER = "static/images/news"

def save_image(file):
    if not file or file.filename == "":
        return None

    filename = secure_filename(file.filename)
    unique_name = str(uuid.uuid4()) + "_" + filename

    path = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(path)

    return unique_name

# LISTAR 
@admin_news_bp.route("/", methods=["GET"])
@admin_required
def list_news():
    news_list = NewsService.get_all()
    return render_template("admin/news/list.html", news_list=news_list)

# CREAR
@admin_news_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_news():

    if request.method == "POST":

        data = request.form.to_dict()

        data["featured"] = True if request.form.get("featured") else False

        image_file = request.files.get("image")
        filename = save_image(image_file)

        if filename:
            data["image"] = filename

        NewsService.create(data)

        flash("Noticia creada correctamente", "success")
        return redirect(url_for("home.index"))

    return render_template("admin/news/form.html")

# EDITAR
@admin_news_bp.route("/edit/<int:news_id>", methods=["GET", "POST"])
@admin_required
def edit_news(news_id):

    news = NewsService.get_by_id(news_id)

    if not news:
        flash("Noticia no encontrada", "danger")
        return redirect(url_for("admin_news.list_news"))

    if request.method == "POST":

        data = request.form.to_dict()

        data["featured"] = True if request.form.get("featured") else False

        image_file = request.files.get("image")
        filename = save_image(image_file)

        if filename:
            data["image"] = filename

        NewsService.update(news_id, data)

        flash("Noticia actualizada correctamente", "success")
        return redirect(url_for("home.index"))

    return render_template("admin/news/form.html", news=news)

# ELIMINAR
@admin_news_bp.route("/delete/<int:news_id>", methods=["POST"])
@admin_required
def delete_news(news_id):

    NewsService.delete(news_id)

    flash("Noticia eliminada correctamente", "success")
    return redirect(url_for("home.index"))