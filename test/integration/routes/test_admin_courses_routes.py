import io
from types import SimpleNamespace

from application.services.course_service import CourseService
from presentation.routes.private.admin_courses_routes import (
    save_image,
    delete_file
)


# Verifica que la lista de cursos cargue correctamente.
def test_list_courses(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_courses",
        lambda: []
    )

    response = admin_client.get("/admin/courses/")

    assert response.status_code == 200


# Verifica que el formulario de creación cargue correctamente.
def test_create_course_get(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_courses",
        lambda: []
    )

    response = admin_client.get("/admin/courses/create")

    assert response.status_code == 200


# Verifica la creación de un curso sin imágenes.
def test_create_course_post(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "create",
        lambda data: True
    )

    response = admin_client.post(
        "/admin/courses/create",
        data={
            "title": "Curso Test",
            "featured": "1"
        },
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la creación de un curso con imágenes.
def test_create_course_post_with_images(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "create",
        lambda data: True
    )

    data = {
        "title": "Curso Test",
        "featured": "1",
        "image": (
            io.BytesIO(b"fake image"),
            "curso.jpg"
        ),
        "certificate_image": (
            io.BytesIO(b"fake image"),
            "cert.jpg"
        )
    }

    response = admin_client.post(
        "/admin/courses/create",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica que el formulario de edición cargue correctamente.
def test_edit_course_get(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_course",
        lambda course_id: {
            "id": course_id,
            "title": "Curso"
        }
    )

    monkeypatch.setattr(
        CourseService,
        "get_moodle_courses",
        lambda: []
    )

    response = admin_client.get("/admin/courses/edit/1")

    assert response.status_code == 200


# Verifica el comportamiento cuando el curso no existe.
def test_edit_course_not_found(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_course",
        lambda course_id: None
    )

    response = admin_client.get(
        "/admin/courses/edit/999",
        follow_redirects=True
    )

    assert response.status_code == 200


# Verifica la actualización de un curso sin imágenes.
def test_edit_course_post(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_course",
        lambda course_id: {
            "id": course_id,
            "title": "Curso"
        }
    )

    monkeypatch.setattr(
        CourseService,
        "update",
        lambda course_id, data: True
    )

    response = admin_client.post(
        "/admin/courses/edit/1",
        data={
            "title": "Nuevo",
            "featured": "1"
        },
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la actualización de un curso con nuevas imágenes.
def test_edit_course_post_with_images(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_moodle_course",
        lambda course_id: {
            "id": course_id,
            "title": "Curso",
            "image": "old.jpg",
            "certificate_image": "old_cert.jpg"
        }
    )

    monkeypatch.setattr(
        CourseService,
        "update",
        lambda course_id, data: True
    )

    data = {
        "title": "Nuevo",
        "image": (
            io.BytesIO(b"fake image"),
            "new.jpg"
        ),
        "certificate_image": (
            io.BytesIO(b"fake image"),
            "new_cert.jpg"
        )
    }

    response = admin_client.post(
        "/admin/courses/edit/1",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la eliminación de un curso existente.
def test_delete_course(admin_client, monkeypatch):
    course = SimpleNamespace(
        image=None,
        certificate_image=None
    )

    monkeypatch.setattr(
        CourseService,
        "get_by_id",
        lambda course_id: course
    )

    monkeypatch.setattr(
        CourseService,
        "delete",
        lambda course_id: True
    )

    response = admin_client.post(
        "/admin/courses/delete/1",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica la eliminación cuando el curso no existe.
def test_delete_course_not_found(admin_client, monkeypatch):
    monkeypatch.setattr(
        CourseService,
        "get_by_id",
        lambda course_id: None
    )

    monkeypatch.setattr(
        CourseService,
        "delete",
        lambda course_id: True
    )

    response = admin_client.post(
        "/admin/courses/delete/1",
        follow_redirects=False
    )

    assert response.status_code == 302


# Verifica que save_image retorne None sin archivo.
def test_save_image_without_file(app):
    with app.app_context():
        result = save_image(None, "courses")

    assert result is None


# Verifica que save_image guarde correctamente un archivo.
def test_save_image_with_file(app, tmp_path):
    class FakeFile:
        filename = "test.jpg"

        def save(self, path):
            with open(path, "wb") as f:
                f.write(b"test")

    app.root_path = str(tmp_path)

    with app.app_context():
        result = save_image(
            FakeFile(),
            "courses"
        )

    assert result.endswith("_test.jpg")


# Verifica la eliminación de un archivo existente.
def test_delete_file_existing(app, tmp_path):
    app.root_path = str(tmp_path)

    folder = (
        tmp_path /
        "static" /
        "images" /
        "courses"
    )

    folder.mkdir(parents=True)

    file_path = folder / "test.jpg"
    file_path.write_text("test")

    with app.app_context():
        delete_file(
            "courses",
            "test.jpg"
        )

    assert not file_path.exists()


# Verifica que delete_file ignore valores None.
def test_delete_file_none(app):
    with app.app_context():
        delete_file(
            "courses",
            None
        )