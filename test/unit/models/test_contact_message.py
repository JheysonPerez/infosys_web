import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.contact_message import ContactMessage


# Fixture que proporciona el contexto de Flask para los tests
@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app


# Fixture con datos válidos reutilizables para los tests
@pytest.fixture
def contact_data():
    return {
        "name": "Jheyson Perez",
        "email": "jheysonperezramirez6@gmail.com",
        "phone": "905921931",
        "message": "Hola, necesito información sobre los cursos."
    }


# Verifica la creación correcta de un mensaje de contacto
def test_create_contact_message(app, contact_data):
    with app.app_context():

        db.session.query(ContactMessage).delete()
        db.session.commit()

        contact = ContactMessage(**contact_data)

        db.session.add(contact)
        db.session.commit()

        saved = ContactMessage.query.filter_by(
            email=contact_data["email"]
        ).first()

        assert saved is not None
        assert saved.name == "Jheyson Perez"
        assert saved.email == "jheysonperezramirez6@gmail.com"
        assert saved.phone == "905921931"
        assert saved.message == "Hola, necesito información sobre los cursos."


# Verifica que la fecha de creación se genere automáticamente
def test_default_created_at(app, contact_data):
    with app.app_context():

        contact = ContactMessage(**contact_data)

        db.session.add(contact)
        db.session.commit()

        saved = ContactMessage.query.filter_by(
            email=contact_data["email"]
        ).first()

        assert isinstance(saved.created_at, datetime)


# Verifica que el teléfono no permita valores nulos
def test_phone_not_nullable(app):
    with app.app_context():

        contact = ContactMessage(
            name="Jheyson Perez",
            email="jheysonperezramirez6@gmail.com",
            message="Mensaje de prueba"
        )

        db.session.add(contact)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que el nombre no permita valores nulos
def test_name_not_nullable(app):
    with app.app_context():

        contact = ContactMessage(
            email="jheysonperezramirez6@gmail.com",
            phone="905921931",
            message="Mensaje de prueba"
        )

        db.session.add(contact)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que el correo no permita valores nulos
def test_email_not_nullable(app):
    with app.app_context():

        contact = ContactMessage(
            name="Jheyson Perez",
            phone="905921931",
            message="Mensaje de prueba"
        )

        db.session.add(contact)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que el mensaje no permita valores nulos
def test_message_not_nullable(app):
    with app.app_context():

        contact = ContactMessage(
            name="Jheyson Perez",
            email="jheysonperezramirez6@gmail.com",
            phone="905921931"
        )

        db.session.add(contact)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()