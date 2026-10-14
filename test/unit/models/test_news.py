import pytest
import os
import shutil
from pathlib import Path
from datetime import date
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.news import News

@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app

@pytest.fixture
def news_data(app):
    source_path = Path(r"C:\Users\jheys\OneDrive\Escritorio\infosys_web\test\fixtures\unit\images\plataforma.jpg")
    static_news_path = Path(app.static_folder) / "images" / "news"
    file_name = "plataforma.jpg"
    file_path = static_news_path / file_name

    try:
        shutil.copy2(source_path, file_path)
    except Exception as e:
        pytest.fail(f"Fallo al copiar el archivo: {e}")

    data = {
        "title": "Nuevo Curso Disponible",
        "content": "Se ha lanzado un nuevo curso de desarrollo web.",
        "expires_at": date(2026, 12, 31),
        "image": file_name,
        "featured": True
    }
    
    yield data


# Verifica que una noticia se cree correctamente
def test_create_news(app, news_data):
    with app.app_context():
        db.session.query(News).delete()
        db.session.commit()

        news = News(**news_data)
        db.session.add(news)
        db.session.commit()

        saved = News.query.filter_by(title=news_data["title"]).first()

        assert saved is not None
        assert saved.image == "plataforma.jpg"
        
        path_en_disco = Path(app.static_folder) / "images" / "news" / saved.image
        assert path_en_disco.exists()


# Verifica que el campo title no permita valores nulos
def test_title_not_nullable(app):
    with app.app_context():
        news = News(
            content="Contenido de prueba",
            expires_at=date(2026, 12, 31),
            image="imagen.jpg"
        )
        db.session.add(news)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# Verifica que el campo content no permita valores nulos
def test_content_not_nullable(app):
    with app.app_context():
        news = News(
            title="Lanzamiento de plataforma digital",
            expires_at=date(2026, 12, 31),
            image="imagen.jpg"
        )
        db.session.add(news)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# Verifica que el campo expires_at no permita valores nulos
def test_expires_at_not_nullable(app):
    with app.app_context():
        news = News(
            title="Título de prueba",
            content="Contenido de prueba",
            image="imagen.jpg"
        )
        db.session.add(news)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# Verifica que el campo image no permita valores nulos
def test_image_not_nullable(app):
    with app.app_context():
        news = News(
            title="Título de prueba",
            content="Contenido de prueba",
            expires_at=date(2026, 12, 31)
        )
        db.session.add(news)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


# Verifica que published_at se asigne automáticamente con la fecha actual
def test_default_published_at(app, news_data):
    with app.app_context():
        db.session.query(News).delete()
        db.session.commit()

        news_data["title"] = "Fecha automática"
        news = News(**news_data)
        db.session.add(news)
        db.session.commit()

        saved = News.query.filter_by(title="Fecha automática").first()
        assert isinstance(saved.published_at, date)
        assert saved.published_at == date.today()


# Verifica que featured tenga False como valor por defecto
def test_default_featured(app, news_data):
    with app.app_context():
        db.session.query(News).delete()
        db.session.commit()

        news_data.pop("featured")
        news_data["title"] = "Featured por defecto"
        news = News(**news_data)
        db.session.add(news)
        db.session.commit()

        saved = News.query.filter_by(title="Featured por defecto").first()
        assert saved.featured is False