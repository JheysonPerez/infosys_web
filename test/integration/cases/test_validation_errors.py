import pytest
from unittest.mock import patch


# CONTACTO
# contacto exitoso
@patch("presentation.routes.public.contact_routes.save_contact_message")
def test_contact_success(mock_save, client):
    response = client.post("/contact/", data={
        "name": "Jheyson Perez",
        "email": "jheyson.xcalibur.15@gmail.com",
        "phone": "905921931",
        "message": "hola"
    })

    assert response.status_code in [302, 303]
    mock_save.assert_called_once()


# error al guardar contacto
@patch("presentation.routes.public.contact_routes.save_contact_message")
def test_contact_error(mock_save, client):
    mock_save.side_effect = Exception("DB error")

    response = client.post("/contact/", data={
        "name": "Jheyson Perez",
        "email": "jheyson.xcalibur.15@gmail.com",
        "phone": "905921931",
        "message": "hola"
    })

    assert response.status_code in [302, 303]


# CURSOS
# listar cursos
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_courses")
def test_list_courses(mock_courses, client):
    mock_courses.return_value = [
        {"id": 1, "duration_weeks": 5},
        {"id": 2, "duration_weeks": 10}
    ]

    response = client.get("/courses")

    assert response.status_code == 200


# curso encontrado
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_found(mock_course, client):
    mock_course.return_value = {
        "id": 1,
        "visible": True
    }

    response = client.get("/courses/1")

    assert response.status_code == 200


# curso no encontrado (404)
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_not_found(mock_course, client):
    mock_course.return_value = None

    response = client.get("/courses/999")

    assert response.status_code == 404


# curso oculto (403)
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_hidden(mock_course, client):
    mock_course.return_value = {
        "id": 1,
        "visible": False
    }

    response = client.get("/courses/1")

    assert response.status_code == 403



# CERTIFICADOS
# búsqueda por código
def test_certificate_by_code(client):
    response = client.get("/certificados?code=2701-2026-ISC")
    assert response.status_code == 200


# búsqueda por dni
def test_certificate_by_dni(client):
    response = client.get("/certificados?dni=72257140")
    assert response.status_code == 200


# búsqueda vacía
def test_certificate_empty_search(client):
    response = client.get("/certificados")
    assert response.status_code == 200