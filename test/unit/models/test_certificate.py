import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db

from domain.models.certificate import Certificate
from domain.models.course import Course


# Fixture que proporciona la aplicación Flask
@pytest.fixture
def app():
    yield flask_app


# Fixture que crea un curso válido para pruebas
@pytest.fixture
def course(app):

    with app.app_context():

        course = Course(
            title="Mantenimiento de Computadoras",
            description="Curso de prueba",
            category="Tecnología",
            level="Intermedio",
            modality="Virtual",

            duration_weeks=8,
            estimated_hours=120,
            price=199.90,

            instructor="Jheyson Perez",
            syllabus="Introducción, mantenimiento y ensamblaje",
            additional_info="Incluye certificado",

            featured=False,
            status="activo",

            image="course.jpg",
            certificate_image="certificate.jpg"
        )

        db.session.add(course)
        db.session.commit()

        yield course

        # teardown
        db.session.rollback()

        Certificate.query.filter_by(
            course_id=course.id
        ).delete()

        db.session.delete(course)
        db.session.commit()


# Fixture con datos válidos reutilizables
@pytest.fixture
def certificate_data(course):

    unique_code = f"C-{uuid4()}"

    return {
        "student_name": "Jheyson Perez Ramirez",
        "student_dni": "72257140",
        "course_id": course.id,
        "code": unique_code,
        "certificate_image":
            f"images/generated_certificates/{unique_code}.jpg",
        "course_name": course.title,
        "start_date": datetime(2024, 1, 10).date(),
        "end_date": datetime(2024, 3, 10).date(),
        "duration": 120,
        "syllabus_snapshot": "Contenido del syllabus del curso",
        "template_snapshot": "Plantilla oficial Info & Sys"
    }


# Verifica creación correcta
def test_create_certificate(app, certificate_data):

    with app.app_context():

        cert = Certificate(**certificate_data)

        db.session.add(cert)
        db.session.commit()

        saved = Certificate.query.filter_by(
            code=certificate_data["code"]
        ).first()

        assert saved is not None
        assert saved.student_name == certificate_data["student_name"]
        assert saved.student_dni == certificate_data["student_dni"]
        assert saved.code == certificate_data["code"]
        assert saved.course_name == certificate_data["course_name"]

        assert (
            saved.certificate_image
            == certificate_data["certificate_image"]
        )

        assert (
            saved.syllabus_snapshot
            == certificate_data["syllabus_snapshot"]
        )

        assert (
            saved.template_snapshot
            == certificate_data["template_snapshot"]
        )

        db.session.delete(saved)
        db.session.commit()


# Verifica valores por defecto
def test_default_values(app, course):

    with app.app_context():

        unique_code = f"C-{uuid4()}"

        cert = Certificate(
            student_name="Jheyson Perez Ramirez",
            student_dni="72257140",
            course_id=course.id,
            code=unique_code,
            certificate_image=(
                f"images/generated_certificates/{unique_code}.jpg"
            ),
            course_name=course.title,
            start_date=datetime(2024, 1, 10).date(),
            end_date=datetime(2024, 3, 10).date(),
            duration=120,
            syllabus_snapshot="Contenido",
            template_snapshot="Plantilla"
        )

        db.session.add(cert)
        db.session.commit()

        saved = Certificate.query.filter_by(
            code=unique_code
        ).first()

        assert saved.type == "generated"
        assert isinstance(saved.issue_date, datetime)

        db.session.delete(saved)
        db.session.commit()


# Verifica unicidad del código
def test_unique_code_constraint(app, course):

    with app.app_context():

        unique_code = f"C-{uuid4()}"

        cert1 = Certificate(
            student_name="Jheyson Perez",
            student_dni="72257140",
            course_id=course.id,
            code=unique_code,
            certificate_image=(
                f"images/generated_certificates/{unique_code}.jpg"
            ),
            course_name=course.title,
            start_date=datetime(2024, 1, 10).date(),
            end_date=datetime(2024, 3, 10).date(),
            duration=120,
            syllabus_snapshot="Contenido",
            template_snapshot="Plantilla"
        )

        cert2 = Certificate(
            student_name="Lorena Perez",
            student_dni="72257138",
            course_id=course.id,
            code=unique_code,
            certificate_image=(
                f"images/generated_certificates/{unique_code}.jpg"
            ),
            course_name=course.title,
            start_date=datetime(2024, 1, 10).date(),
            end_date=datetime(2024, 3, 10).date(),
            duration=120,
            syllabus_snapshot="Contenido",
            template_snapshot="Plantilla"
        )

        db.session.add(cert1)
        db.session.commit()

        db.session.add(cert2)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        db.session.delete(cert1)
        db.session.commit()


# Verifica certificate_image obligatorio
def test_certificate_image_not_nullable(app, course):

    with app.app_context():

        unique_code = f"C-{uuid4()}"

        cert = Certificate(
            student_name="Jheyson Perez",
            student_dni="72257140",
            course_id=course.id,
            code=unique_code,
            course_name=course.title,
            start_date=datetime(2024, 1, 10).date(),
            end_date=datetime(2024, 3, 10).date(),
            duration=120,
            syllabus_snapshot="Contenido",
            template_snapshot="Plantilla"
        )

        db.session.add(cert)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica campos obligatorios
def test_required_fields(app):

    with app.app_context():

        cert = Certificate()

        db.session.add(cert)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()