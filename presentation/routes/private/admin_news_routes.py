from flask import Blueprint, render_template, request, redirect, url_for, flash
from infosys_web.presentation.routes.private.admin_guard import admin_required
from infosys_web.application.services.news_service import NewsService

admin_news_bp = Blueprint(
    "admin_news",
    __name__,
    url_prefix="/admin/news"
)
# LISTAR
@admin_news_bp.route("/", methods=["GET"])
@admin_required
def list_news():
    return redirect(url_for("home.index"))

# CREAR
@admin_news_bp.route("/create", methods=["GET", "POST"])
@admin_required
def create_news():
    if request.method == "POST":
        NewsService.create(request.form.to_dict())
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
        return redirect(url_for("home.index")) 

    if request.method == "POST":
        NewsService.update(news_id, request.form.to_dict())
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