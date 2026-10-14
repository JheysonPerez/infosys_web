from unittest.mock import patch


# Verifica que la lista de cursos cargue correctamente.
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_courses")
def test_list_courses(mock_get_moodle_courses, client):

    mock_get_moodle_courses.return_value = []

    response = client.get("/courses")

    assert response.status_code == 200


# Verifica que se muestre el detalle de un curso existente.
@patch("presentation.routes.public.course_routes.StatisticService.register_event")
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_success(
    mock_get_moodle_course,
    mock_register_event,
    client
):

    mock_get_moodle_course.return_value = {
        "id": 1,
        "fullname": "Curso Prueba ",
        "visible": True
    }

    response = client.get("/courses/1")

    assert response.status_code == 200

    mock_register_event.assert_called_once_with(
        "course_view",
        1
    )


# Verifica que se retorne 404 cuando el curso no existe.
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_not_found(
    mock_get_moodle_course,
    client
):

    mock_get_moodle_course.return_value = None

    response = client.get("/courses/999")

    assert response.status_code == 404


# Verifica que un curso oculto no pueda ser visualizado por usuarios no administradores.
@patch("presentation.routes.public.course_routes.CourseService.get_moodle_course")
def test_course_detail_hidden_course(
    mock_get_moodle_course,
    client
):

    mock_get_moodle_course.return_value = {
        "id": 1,
        "fullname": "Curso Oculto",
        "visible": False
    }

    response = client.get("/courses/1")

    assert response.status_code == 403

# Verifica la generación correcta de rangos de duración para cursos válidos.
def test_generate_duration_ranges():

    from presentation.routes.public.course_routes import generate_duration_ranges

    courses = [
        {"duration_weeks": 2},
        {"duration_weeks": 5},
        {"duration_weeks": 10}
    ]

    ranges = generate_duration_ranges(courses)

    assert ranges == [
        (1, 4),
        (5, 8),
        (9, 12)
    ]


# Verifica que se ignoren duraciones inválidas al generar rangos.
def test_generate_duration_ranges_invalid_values():

    from presentation.routes.public.course_routes import generate_duration_ranges

    courses = [
        {"duration_weeks": "abc"},
        {"duration_weeks": None},
        {},
    ]

    ranges = generate_duration_ranges(courses)

    assert ranges == []


# Verifica que no se generen rangos cuando no existen duraciones válidas.
def test_generate_duration_ranges_empty():

    from presentation.routes.public.course_routes import generate_duration_ranges

    assert generate_duration_ranges([]) == []