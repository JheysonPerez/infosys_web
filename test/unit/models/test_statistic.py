import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.statistic import Statistic


# Fixture que proporciona el contexto de Flask para los tests
@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app


# Fixture con datos válidos reutilizables para los tests
@pytest.fixture
def statistic_data():
    return {
        "event_type": "course_view",
        "reference_id": 1
    }


# Verifica la creación correcta de una estadística
def test_create_statistic(app, statistic_data):
    with app.app_context():

        db.session.query(Statistic).delete()
        db.session.commit()

        statistic = Statistic(**statistic_data)

        db.session.add(statistic)
        db.session.commit()

        saved = Statistic.query.filter_by(
            event_type=statistic_data["event_type"]
        ).first()

        assert saved is not None
        assert saved.event_type == "course_view"
        assert saved.reference_id == 1


# Verifica que event_type no permita valores nulos
def test_event_type_not_nullable(app):
    with app.app_context():

        statistic = Statistic(
            reference_id=1
        )

        db.session.add(statistic)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que created_at se genere automáticamente
def test_default_created_at(app, statistic_data):
    with app.app_context():

        db.session.query(Statistic).delete()
        db.session.commit()

        statistic_data["event_type"] = "service_view"

        statistic = Statistic(**statistic_data)

        db.session.add(statistic)
        db.session.commit()

        saved = Statistic.query.filter_by(
            event_type="service_view"
        ).first()

        assert isinstance(saved.created_at, datetime)


# Verifica que reference_id pueda ser nulo
def test_reference_id_nullable(app):
    with app.app_context():

        statistic = Statistic(
            event_type="visit"
        )

        db.session.add(statistic)
        db.session.commit()

        saved = Statistic.query.filter_by(
            event_type="visit"
        ).first()

        assert saved is not None
        assert saved.reference_id is None