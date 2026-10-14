import pytest
import shutil
from pathlib import Path
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.course import Course


# Fixture que proporciona el contexto de Flask para los tests
@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def course_data(app):
    source_image_path = Path(r"C:\Users\jheys\OneDrive\Escritorio\infosys_web\test\fixtures\unit\images\curso.jpg")
    source_certificate_path = Path(r"C:\Users\jheys\OneDrive\Escritorio\infosys_web\test\fixtures\unit\images\certificado.jpg")
    
    static_courses_path = Path(app.static_folder) / "images" / "courses"
    static_certificates_path = Path(app.static_folder) / "images" / "certificates"
    
    image_name = "curso.jpg"
    certificate_name = "certificado.jpg"
    
    image_path = static_courses_path / image_name
    certificate_path = static_certificates_path / certificate_name

    try:
        shutil.copy2(source_image_path, image_path)
        shutil.copy2(source_certificate_path, certificate_path)
    except Exception as e:
        pytest.fail(f"Fallo al copiar los archivos: {e}")

    data = {
        "title": "Python para Principiantes",
        "description": "Curso básico de Python.",
        "category": "Programación",
        "level": "Básico",
        "modality": "Virtual",
        "duration_weeks": 8,
        "estimated_hours": 40,
        "instructor": "Jheyson Perez",
        "syllabus": "Introducción, variables, funciones y POO.",
        "additional_info": "Incluye certificado.",
        "price": Decimal("199.90"),
        "featured": True,
        "status": "activo",
        "image": image_name,
        "certificate_image": certificate_name
    }
    
    yield data


# Verifica la creación correcta de un curso
def test_create_course(app, course_data):
    with app.app_context():

        db.session.query(Course).delete()
        db.session.commit()

        course = Course(**course_data)

        db.session.add(course)
        db.session.commit()

        saved = Course.query.filter_by(
            title=course_data["title"]
        ).first()

        print(course.image)
        print(course.certificate_image)

        assert saved is not None
        assert saved.title == "Python para Principiantes"
        assert saved.description == "Curso básico de Python."
        assert saved.category == "Programación"
        assert saved.level == "Básico"
        assert saved.modality == "Virtual"
        assert saved.duration_weeks == 8
        assert saved.estimated_hours == 40
        assert saved.instructor == "Jheyson Perez"
        assert saved.syllabus == (
            "Introducción, variables, funciones y POO."
        )
        assert saved.additional_info == "Incluye certificado."
        assert saved.price == Decimal("199.90")
        assert saved.featured is True
        assert saved.status == "activo"
        assert saved.image == "curso.jpg"
        assert saved.certificate_image == "certificado.jpg"

        image_disk_path = (
            Path(app.static_folder)
            / "images"
            / "courses"
            / saved.image
        )

        certificate_disk_path = (
            Path(app.static_folder)
            / "images"
            / "certificates"
            / saved.certificate_image
        )

        assert image_disk_path.exists()
        assert certificate_disk_path.exists()


# Verifica que el título no permita valores nulos
def test_title_not_nullable(app):
    with app.app_context():

        course = Course(
            description="Curso de prueba",
            category="Programación",
            level="Básico",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg",
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que description no permita valores nulos
def test_description_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            category="Programación",
            level="Básico",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg",
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que category no permita valores nulos
def test_category_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            description="Descripción",
            level="Básico",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg",
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que level no permita valores nulos
def test_level_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            description="Descripción",
            category="Programación",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg",
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que modality no permita valores nulos
def test_modality_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            description="Descripción",
            category="Programación",
            level="Básico",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg",
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que image no permita valores nulos
def test_image_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            description="Descripción",
            category="Programación",
            level="Básico",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            certificate_image="certificado.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que certificate_image no permita valores nulos
def test_certificate_image_not_nullable(app):
    with app.app_context():

        course = Course(
            title="Curso",
            description="Descripción",
            category="Programación",
            level="Básico",
            modality="Virtual",
            duration_weeks=4,
            estimated_hours=20,
            instructor="Instructor",
            syllabus="Temario",
            additional_info="Información",
            price=Decimal("50.00"),
            image="imagen.jpg"
        )

        db.session.add(course)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que el valor por defecto de featured sea False
def test_default_featured(app, course_data):
    with app.app_context():

        db.session.query(Course).delete()
        db.session.commit()

        course_data.pop("featured")
        course_data["title"] = "Curso Default Featured"

        course = Course(**course_data)

        db.session.add(course)
        db.session.commit()

        saved = Course.query.filter_by(
            title="Curso Default Featured"
        ).first()

        assert saved.featured is False


# Verifica que el valor por defecto de status sea 'activo'
def test_default_status(app, course_data):
    with app.app_context():

        db.session.query(Course).delete()
        db.session.commit()

        course_data.pop("status")
        course_data["title"] = "Curso Default Status"

        course = Course(**course_data)

        db.session.add(course)
        db.session.commit()

        saved = Course.query.filter_by(
            title="Curso Default Status"
        ).first()

        assert saved.status == "activo"


# Verifica que el precio pueda almacenarse correctamente
def test_price_field(app, course_data):
    with app.app_context():

        db.session.query(Course).delete()
        db.session.commit()

        course_data["title"] = "Curso Precio"

        course = Course(**course_data)

        db.session.add(course)
        db.session.commit()

        saved = Course.query.filter_by(
            title="Curso Precio"
        ).first()

        assert isinstance(saved.price, Decimal)
        assert saved.price == Decimal("199.90")