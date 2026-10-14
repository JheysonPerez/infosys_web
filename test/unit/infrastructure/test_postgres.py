import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from infrastructure.database.postgres import db
from config import Config


@pytest.fixture
def app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    return app


# Verifica que db sea una instancia de SQLAlchemy
def test_db_is_sqlalchemy_instance():
    assert isinstance(db, SQLAlchemy)


# Verifica que SQLAlchemy se inicialice correctamente con Flask
def test_db_initializes_with_flask(app):
    with app.app_context():
        assert db.engine is not None


# Verifica que exista una URI de conexión configurada
def test_database_uri_exists():
    assert Config.SQLALCHEMY_DATABASE_URI is not None


# Verifica que track modifications esté deshabilitado
def test_sqlalchemy_track_modifications_disabled():
    assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False


# Verifica que las opciones del motor estén configuradas
def test_engine_options_exist():
    assert Config.SQLALCHEMY_ENGINE_OPTIONS["pool_pre_ping"] is True
    assert Config.SQLALCHEMY_ENGINE_OPTIONS["pool_recycle"] == 300