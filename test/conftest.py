import pytest
from app import app as flask_app


# crea la app en modo testing
@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["LOGIN_DISABLED"] = True
    return flask_app


# cliente de pruebas
@pytest.fixture
def client(app):
    return app.test_client()


# cliente autenticado como administrador
@pytest.fixture
def admin_client(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "email": "jheyson.xcalibur.15@gmail.com"
        }

    return client