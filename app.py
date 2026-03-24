from flask import Flask
from dotenv import load_dotenv
from flask import session
import os

load_dotenv()

from config import Config
from infosys_web.infrastructure.database.postgres import db
from infosys_web.infrastructure.mail.smtp import mail
from infosys_web.presentation.routes.public.home_routes import home_bp
from infosys_web.presentation.routes.private.admin_team_routes import admin_team_bp
from infosys_web.presentation.routes.private.admin_news_routes import admin_news_bp
from infosys_web.presentation.routes.public.course_routes import course_bp
from infosys_web.presentation.routes.private.admin_courses_routes import admin_courses_bp
from infosys_web.presentation.routes.public.services_routes import services_bp
from infosys_web.presentation.routes.public.about_routes import about_bp
from infosys_web.presentation.routes.public.contact_routes import contact_bp
from infosys_web.presentation.routes.public.auth_routes import auth_bp, oauth
from infosys_web.presentation.routes.private.admin_routes import admin_bp
from infosys_web.presentation.routes.private.admin_services_routes import admin_services_bp

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
    app.run(debug=True)
