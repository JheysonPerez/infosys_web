from flask import Flask, session
from dotenv import load_dotenv
import os

load_dotenv()

from config import Config
from infrastructure.database.postgres import db
from infrastructure.mail.smtp import mail

from domain.models.statistic import Statistic
from domain.models.course import Course
from domain.models.news import News
from domain.models.services import Service
from domain.models.team_member import TeamMember
from domain.models.contact_message import ContactMessage

from presentation.routes.public.home_routes import home_bp
from presentation.routes.private.admin_team_routes import admin_team_bp
from presentation.routes.private.admin_news_routes import admin_news_bp
from presentation.routes.public.course_routes import course_bp
from presentation.routes.private.admin_courses_routes import admin_courses_bp
from presentation.routes.public.services_routes import services_bp
from presentation.routes.public.about_routes import about_bp
from presentation.routes.public.contact_routes import contact_bp
from presentation.routes.public.auth_routes import auth_bp, oauth
from presentation.routes.private.admin_routes import admin_bp
from presentation.routes.private.admin_services_routes import admin_services_bp

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "presentation", "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    app.config.from_object(Config)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super_secret_key")
    app.config["SESSION_COOKIE_NAME"] = "infosys_session"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["JSON_AS_ASCII"] = False

    @app.after_request
    def force_utf8(response):
        if response.content_type.startswith("text/html"):
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response

    db.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_user():
        return dict(
            user=session.get("user"),
            is_admin=session.get("is_admin", False)
        )

    app.register_blueprint(home_bp)
    app.register_blueprint(admin_news_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(admin_courses_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(admin_services_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(admin_team_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))