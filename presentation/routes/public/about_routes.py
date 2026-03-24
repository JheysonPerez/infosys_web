from flask import Blueprint, render_template, session
from infosys_web.application.services.team_service import TeamService

about_bp = Blueprint("about", __name__)

# RUTA SOBRE NOSOTROS
@about_bp.route("/about")
def about_page():
    team = TeamService.get_all_active()

    for member in team:
        member.socials = TeamService.build_social_links(member)

    return render_template(
        "about/about.html",
        team=team,
        is_admin=session.get("is_admin", False)
    )