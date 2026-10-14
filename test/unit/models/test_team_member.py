import pytest
import shutil
from pathlib import Path
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.team_member import TeamMember


# Fixture que proporciona el contexto de Flask para los tests
@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app


# Fixture con datos válidos reutilizables para los tests
@pytest.fixture
def member_data(app):

    source_image_path = Path(
        r"C:\Users\jheys\OneDrive\Escritorio\infosys_web\test\fixtures\unit\images\jheyson.jpg"
    )

    static_team_path = (
        Path(app.static_folder)
        / "images"
        / "team"
    )

    static_team_path.mkdir(
        parents=True,
        exist_ok=True
    )

    image_name = "jheyson.jpg"

    image_path = static_team_path / image_name

    try:
        shutil.copy2(
            source_image_path,
            image_path
        )

    except Exception as e:
        pytest.fail(
            f"Fallo al copiar la imagen: {e}"
        )

    return {
        "full_name": "Jheyson Perez",
        "role": "Practicante Pre Profesional",
        "image": image_name,
        "instagram": "https://www.instagram.com/jheysonperez_15/",
        "facebook": "https://www.facebook.com/jheyson.perez.560",
        "whatsapp": "https://wa.me/905921931",
        "tiktok": "https://www.tiktok.com/@archiegod?lang=es-419",
        "order": 1,
        "active": True
    }


# Verifica la creación correcta de un miembro del equipo
def test_create_team_member(app, member_data):
    with app.app_context():

        db.session.query(TeamMember).delete()
        db.session.commit()

        member = TeamMember(**member_data)

        db.session.add(member)
        db.session.commit()

        saved = TeamMember.query.filter_by(
            full_name=member_data["full_name"]
        ).first()

        assert saved is not None
        assert saved.full_name == "Jheyson Perez"
        assert saved.role == "Practicante Pre Profesional"
        assert saved.image == "jheyson.jpg"
        assert saved.instagram == "https://www.instagram.com/jheysonperez_15/"
        assert saved.facebook == "https://www.facebook.com/jheyson.perez.560"
        assert saved.whatsapp == "https://wa.me/905921931"
        assert saved.tiktok == "https://www.tiktok.com/@archiegod?lang=es-419"
        assert saved.order == 1
        assert saved.active is True

        image_disk_path = (
            Path(app.static_folder)
            / "images"
            / "team"
            / saved.image
        )

        assert image_disk_path.exists()


# Verifica que full_name no permita valores nulos
def test_full_name_not_nullable(app):
    with app.app_context():

        member = TeamMember(
            role="Practicante Pre Profesional",
            image="imagen.jpg"
        )

        db.session.add(member)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que role no permita valores nulos
def test_role_not_nullable(app):
    with app.app_context():

        member = TeamMember(
            full_name="Jheyson Perez",
            image="imagen.jpg"
        )

        db.session.add(member)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que image no permita valores nulos
def test_image_not_nullable(app):
    with app.app_context():

        member = TeamMember(
            full_name="Jheyson Perez",
            role="Practicante Pre Profesional"
        )

        db.session.add(member)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que created_at se genere automáticamente
def test_default_created_at(app, member_data):
    with app.app_context():

        db.session.query(TeamMember).delete()
        db.session.commit()

        member_data["full_name"] = "Fecha Automática"

        member = TeamMember(**member_data)

        db.session.add(member)
        db.session.commit()

        saved = TeamMember.query.filter_by(
            full_name="Fecha Automática"
        ).first()

        assert isinstance(saved.created_at, datetime)


# Verifica que el valor por defecto de order sea 1
def test_default_order(app, member_data):
    with app.app_context():

        db.session.query(TeamMember).delete()
        db.session.commit()

        member_data.pop("order")
        member_data["full_name"] = "Default Order"

        member = TeamMember(**member_data)

        db.session.add(member)
        db.session.commit()

        saved = TeamMember.query.filter_by(
            full_name="Default Order"
        ).first()

        assert saved.order == 1


# Verifica que el valor por defecto de active sea True
def test_default_active(app, member_data):
    with app.app_context():

        db.session.query(TeamMember).delete()
        db.session.commit()

        member_data.pop("active")
        member_data["full_name"] = "Jheyson Perez"

        member = TeamMember(**member_data)

        db.session.add(member)
        db.session.commit()

        saved = TeamMember.query.filter_by(
            full_name="Jheyson Perez"
        ).first()

        assert saved.active is True


# Verifica que las redes sociales puedan ser nulas
def test_nullable_social_media_fields(app):
    with app.app_context():

        member = TeamMember(
            full_name="Jheyson Perez Sin Redes",
            role="Practicante Pre Profesional",
            image="jheyson.jpg",
            order=2
        )

        db.session.add(member)
        db.session.commit()

        saved = TeamMember.query.filter_by(
            full_name="Jheyson Perez Sin Redes"
        ).first()

        assert saved is not None
        assert saved.instagram is None
        assert saved.facebook is None
        assert saved.whatsapp is None
        assert saved.tiktok is None