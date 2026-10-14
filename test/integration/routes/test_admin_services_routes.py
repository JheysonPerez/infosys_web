import io
from types import SimpleNamespace

from application.services.service_service import ServiceService
from presentation.routes.private.admin_services_routes import (
    save_image,
    UPLOAD_FOLDER
)


MOCK_SERVICE = SimpleNamespace(
    id=1,
    name="Consultoría TI",
    description="Servicio de consultoría tecnológica",
    service_type="Consultoría",
    estimated_duration="40 horas",
    delivery_mode="Virtual",
    additional_info="Incluye soporte",
    price=1500.00,
    featured=True,
    status="activo",
    image="service.jpg"
)


# Verifica que la lista de servicios cargue correctamente.
def test_list_services(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "filter_services",
        lambda **kwargs: [MOCK_SERVICE]
    )

    monkeypatch.setattr(
        ServiceService,
        "get_service_types",
        lambda: ["Consultoría"]
    )

    monkeypatch.setattr(
        ServiceService,
        "get_modalities",
        lambda: ["Virtual"]
    )

    monkeypatch.setattr(
        ServiceService,
        "get_duration_ranges",
        lambda services: ["40 horas"]
    )

    response = admin_client.get("/admin/services/")

    assert response.status_code == 200


# Verifica que el formulario de creación cargue correctamente.
def test_create_service_get(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_service_types",
        lambda: ["Consultoría"]
    )

    response = admin_client.get("/admin/services/create")

    assert response.status_code == 200


# Verifica la creación de un servicio sin imagen.
def test_create_service_post(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "create",
        lambda data: True
    )

    response = admin_client.post(
        "/admin/services/create",
        data={
            "name": "Servicio Test",
            "description": "Descripción del servicio de prueba",
            "service_type": "Consultoría",
            "estimated_duration": "40 horas",
            "delivery_mode": "Virtual",
            "additional_info": "Información adicional",
            "price": "100.00",
            "status": "activo",
            "featured": "1"
        },
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la creación de un servicio con imagen.
def test_create_service_post_with_image(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "create",
        lambda data: True
    )

    response = admin_client.post(
        "/admin/services/create",
        data={
            "name": "Servicio Test",
            "description": "Descripción del servicio de prueba",
            "service_type": "Consultoría",
            "estimated_duration": "40 horas",
            "delivery_mode": "Virtual",
            "additional_info": "Información adicional",
            "price": "100.00",
            "status": "activo",
            "image": (
                io.BytesIO(b"fake image"),
                "service.jpg"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica que el formulario de edición cargue correctamente.
def test_edit_service_get(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: MOCK_SERVICE
    )

    monkeypatch.setattr(
        ServiceService,
        "get_service_types",
        lambda: ["Consultoría"]
    )

    response = admin_client.get("/admin/services/edit/1")

    assert response.status_code == 200


# Verifica el comportamiento cuando el servicio no existe.
def test_edit_service_not_found(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: None
    )

    response = admin_client.get(
        "/admin/services/edit/999",
        follow_redirects=True
    )

    assert response.status_code == 200


# Verifica la actualización de un servicio sin imagen.
def test_edit_service_post(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: MOCK_SERVICE
    )

    monkeypatch.setattr(
        ServiceService,
        "update",
        lambda service_id, data: True
    )

    response = admin_client.post(
        "/admin/services/edit/1",
        data={
            "name": "Servicio Editado",
            "description": "Nueva descripción",
            "service_type": "Consultoría",
            "estimated_duration": "20 horas",
            "delivery_mode": "Presencial",
            "additional_info": "Nueva información",
            "price": "200.00",
            "status": "activo"
        },
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la actualización de un servicio con imagen nueva.
def test_edit_service_post_with_image(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: MOCK_SERVICE
    )

    monkeypatch.setattr(
        ServiceService,
        "update",
        lambda service_id, data: True
    )

    response = admin_client.post(
        "/admin/services/edit/1",
        data={
            "name": "Servicio Editado",
            "description": "Nueva descripción",
            "service_type": "Consultoría",
            "estimated_duration": "20 horas",
            "delivery_mode": "Virtual",
            "additional_info": "Nueva información",
            "price": "200.00",
            "status": "activo",
            "image": (
                io.BytesIO(b"fake image"),
                "new.jpg"
            )
        },
        content_type="multipart/form-data",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la eliminación de un servicio existente.
def test_delete_service(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: MOCK_SERVICE
    )

    monkeypatch.setattr(
        ServiceService,
        "delete",
        lambda service_id: True
    )

    response = admin_client.post(
        "/admin/services/delete/1",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la eliminación cuando el servicio no existe.
def test_delete_service_not_found(admin_client, monkeypatch):
    monkeypatch.setattr(
        ServiceService,
        "get_by_id",
        lambda service_id: None
    )

    monkeypatch.setattr(
        ServiceService,
        "delete",
        lambda service_id: True
    )

    response = admin_client.post(
        "/admin/services/delete/1",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica que save_image retorne None sin archivo.
def test_save_image_without_file(app):
    with app.app_context():
        result = save_image(None)

    assert result is None


# Verifica que save_image guarde correctamente un archivo.
def test_save_image_with_file(app, tmp_path):
    class FakeFile:
        filename = "test.jpg"

        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"test")

    original_root = app.root_path
    app.root_path = str(tmp_path)

    try:
        with app.app_context():
            result = save_image(FakeFile())

        file_path = (
            tmp_path /
            UPLOAD_FOLDER /
            "test.jpg"
        )

        assert file_path.exists()
        assert result == "test.jpg"

    finally:
        app.root_path = original_root