from unittest.mock import patch
from flask import Flask

from presentation.routes.private.admin_guard import admin_required


# Permite acceso cuando el usuario es administrador
def test_admin_required_admin_user():

    app = Flask(__name__)
    app.secret_key = "test"

    @app.route("/protected")
    @admin_required
    def protected():
        return "OK"

    with app.test_request_context():

        from flask import session

        session["user"] = {
            "email": "jheyson.xcalibur.15@gmail.com"
        }

        assert protected() == "OK"


# Redirige al login cuando no existe usuario en sesión
@patch("presentation.routes.private.admin_guard.url_for")
@patch("presentation.routes.private.admin_guard.redirect")
def test_admin_required_without_user(
    mock_redirect,
    mock_url_for
):

    app = Flask(__name__)
    app.secret_key = "test"

    mock_url_for.return_value = "/login"

    @admin_required
    def protected():
        return "OK"

    with app.test_request_context():

        protected()

        mock_url_for.assert_called_once_with(
            "auth.login_google"
        )

        mock_redirect.assert_called_once_with(
            "/login"
        )


# Redirige al logout cuando el usuario no es administrador
@patch("presentation.routes.private.admin_guard.url_for")
@patch("presentation.routes.private.admin_guard.redirect")
def test_admin_required_non_admin(
    mock_redirect,
    mock_url_for
):

    app = Flask(__name__)
    app.secret_key = "test"

    mock_url_for.return_value = "/logout"

    @admin_required
    def protected():
        return "OK"

    with app.test_request_context():

        from flask import session

        session["user"] = {
            "email": "usuario@gmail.com"
        }

        protected()

        mock_url_for.assert_called_once_with(
            "auth.logout"
        )

        mock_redirect.assert_called_once_with(
            "/logout"
        )