import pytest
import shutil
from pathlib import Path
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app import app as flask_app
from infrastructure.database.postgres import db
from domain.models.services import Service


# Fixture que proporciona el contexto de Flask para los tests
@pytest.fixture
def app():
    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def service_data(app):
    source_path = Path(
        r"C:\Users\jheys\OneDrive\Escritorio\infosys_web\test\fixtures\unit\images\servicio.jpg"
    )
    static_services_path = Path(app.static_folder) / "images" / "services"
    file_name = "servicio.jpg"
    file_path = static_services_path / file_name

    try:
        shutil.copy2(source_path, file_path)
    except Exception as e:
        pytest.fail(f"Fallo al copiar el archivo: {e}")

    data = {
        "name": "Desarrollo Web Profesional",
        "description": "Servicio de creación de páginas web.",
        "service_type": "Desarrollo",
        "estimated_duration": "Segun requerimientos",
        "delivery_mode": "Virtual",
        "additional_info": "Incluye soporte técnico.",
        "price": Decimal("499.90"),
        "featured": True,
        "status": "activo",
        "image": file_name,
    }

    yield data


# Verifica la creación correcta de un servicio
def test_create_service(app, service_data):
    with app.app_context():

        db.session.query(Service).delete()
        db.session.commit()

        service = Service(**service_data)

        db.session.add(service)
        db.session.commit()

        saved = Service.query.filter_by(
            name=service_data["name"]
        ).first()

        assert saved is not None
        assert saved.name == "Desarrollo Web Profesional"
        assert saved.description == (
            "Servicio de creación de páginas web."
        )
        assert saved.service_type == "Desarrollo"
        assert saved.estimated_duration == "Segun requerimientos"
        assert saved.delivery_mode == "Virtual"
        assert saved.additional_info == (
            "Incluye soporte técnico."
        )
        assert saved.price == Decimal("499.90")
        assert saved.featured is True
        assert saved.status == "activo"
        assert saved.image == "servicio.jpg"

        path_en_disco = (
            Path(app.static_folder)
            / "images"
            / "services"
            / saved.image
        )

        assert path_en_disco.exists()


# Verifica que name no permita valores nulos
def test_name_not_nullable(app):
    with app.app_context():

        service = Service(
            description="Descripción",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            additional_info="Información",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que description no permita valores nulos
def test_description_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            additional_info="Información",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que service_type no permita valores nulos
def test_service_type_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            additional_info="Información",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que estimated_duration no permita valores nulos
def test_estimated_duration_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            service_type="Desarrollo",
            delivery_mode="Virtual",
            additional_info="Información",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que delivery_mode no permita valores nulos
def test_delivery_mode_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            additional_info="Información",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que additional_info no permita valores nulos
def test_additional_info_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            price=Decimal("100.00"),
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que price no permita valores nulos
def test_price_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            additional_info="Información",
            image="imagen.jpg"
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que image no permita valores nulos
def test_image_not_nullable(app):
    with app.app_context():

        service = Service(
            name="Servicio",
            description="Descripción",
            service_type="Desarrollo",
            estimated_duration="Segun requerimientos",
            delivery_mode="Virtual",
            additional_info="Información",
            price=Decimal("100.00")
        )

        db.session.add(service)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()


# Verifica que el valor por defecto de featured sea False
def test_default_featured(app, service_data):
    with app.app_context():

        db.session.query(Service).delete()
        db.session.commit()

        service_data.pop("featured")
        service_data["name"] = "Servicio Featured"

        service = Service(**service_data)

        db.session.add(service)
        db.session.commit()

        saved = Service.query.filter_by(
            name="Servicio Featured"
        ).first()

        assert saved.featured is False


# Verifica que el valor por defecto de status sea 'activo'
def test_default_status(app, service_data):
    with app.app_context():

        db.session.query(Service).delete()
        db.session.commit()

        service_data.pop("status")
        service_data["name"] = "Servicio Status"

        service = Service(**service_data)

        db.session.add(service)
        db.session.commit()

        saved = Service.query.filter_by(
            name="Servicio Status"
        ).first()

        assert saved.status == "activo"


# Verifica que el precio pueda almacenarse correctamente
def test_price_field(app, service_data):
    with app.app_context():

        db.session.query(Service).delete()
        db.session.commit()

        service_data["name"] = "Servicio Precio"

        service = Service(**service_data)

        db.session.add(service)
        db.session.commit()

        saved = Service.query.filter_by(
            name="Servicio Precio"
        ).first()

        assert isinstance(saved.price, Decimal)
        assert saved.price == Decimal("499.90")