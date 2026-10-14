from unittest.mock import MagicMock, patch
from application.services.course_service import CourseService


# Obtener todos los cursos
@patch("application.services.course_service.Course")
def test_get_all(mock_course):

    expected = [MagicMock(), MagicMock()]

    mock_course.query.all.return_value = expected

    result = CourseService.get_all()

    assert result == expected


# Obtener cursos activos
@patch("application.services.course_service.Course")
def test_get_active(mock_course):

    expected = [MagicMock()]

    mock_course.query.filter_by.return_value.all.return_value = expected

    result = CourseService.get_active()

    assert result == expected


# Obtener curso por ID
@patch("application.services.course_service.Course")
def test_get_by_id(mock_course):

    course = MagicMock()

    mock_course.query.get.return_value = course

    result = CourseService.get_by_id(1)

    assert result == course


# Obtener curso Moodle con datos locales
@patch("application.services.course_service.Course")
@patch("application.services.course_service.MoodleAPI")
def test_get_moodle_course_with_local_data(mock_moodle, mock_course):

    local_course = MagicMock()
    local_course.price = 150
    local_course.modality = "Virtual"
    local_course.level = "Intermedio"
    local_course.duration_weeks = 8
    local_course.estimated_hours = 40
    local_course.instructor = "Jheyson Perez"
    local_course.image = "curso.jpg"
    local_course.certificate_image = "cert.jpg"
    local_course.syllabus = "Temario"
    local_course.additional_info = "Info"
    local_course.featured = True
    local_course.status = "activo"
    local_course.category = "Programación"

    mock_moodle.get_course.return_value = {
        "courses": [{"id": 1, "fullname": "Python"}]
    }

    mock_course.query.filter_by.return_value.first.return_value = local_course

    result = CourseService.get_moodle_course(1)

    assert result["price"] == 150
    assert result["category"] == "Programación"


# Obtener curso Moodle sin datos locales
@patch("application.services.course_service.Course")
@patch("application.services.course_service.MoodleAPI")
def test_get_moodle_course_without_local_data(mock_moodle, mock_course):

    mock_moodle.get_course.return_value = {
        "courses": [{"id": 1, "fullname": "Python"}]
    }

    mock_course.query.filter_by.return_value.first.return_value = None

    result = CourseService.get_moodle_course(1)

    assert result["price"] is None
    assert result["modality"] == "Virtual"
    assert result["status"] == "activo"


# Moodle lanza excepción
@patch("application.services.course_service.MoodleAPI")
def test_get_moodle_course_exception(mock_moodle):

    mock_moodle.get_course.side_effect = Exception()

    result = CourseService.get_moodle_course(1)

    assert result is None


# Obtener múltiples cursos Moodle con datos locales
@patch("application.services.course_service.Course")
@patch("application.services.course_service.MoodleAPI")
def test_get_moodle_courses(mock_moodle, mock_course):

    local_course = MagicMock()
    local_course.moodle_course_id = 1
    local_course.price = 200
    local_course.modality = "Virtual"
    local_course.level = "Avanzado"
    local_course.duration_weeks = 10
    local_course.estimated_hours = 50
    local_course.instructor = "Jheyson"
    local_course.image = "img.jpg"
    local_course.certificate_image = "cert.jpg"
    local_course.syllabus = "Temario"
    local_course.additional_info = "Info"
    local_course.featured = True
    local_course.status = "activo"
    local_course.category = "TI"

    mock_moodle.get_courses.return_value = [
        {"id": 1, "fullname": "Python"},
        {"id": 2, "fullname": "Java"}
    ]

    mock_course.query.all.return_value = [local_course]

    result = CourseService.get_moodle_courses()

    assert len(result) == 2
    assert result[0]["price"] == 200
    assert result[1]["price"] is None


# Moodle cursos excepción
@patch("application.services.course_service.MoodleAPI")
def test_get_moodle_courses_exception(mock_moodle):

    mock_moodle.get_courses.side_effect = Exception()

    result = CourseService.get_moodle_courses()

    assert result == []


# Filtrar cursos
@patch("application.services.course_service.Course")
@patch("application.services.course_service.db")
def test_filter_courses(mock_db, mock_course):

    expected = [MagicMock()]

    query = MagicMock()
    mock_course.query = query

    query.filter.return_value = query
    query.all.return_value = expected

    result = CourseService.filter_courses(
        search="Python",
        category="TI",
        modality="Virtual",
        level="Basico",
        duration="4-8"
    )

    assert result == expected


# Crear curso
@patch("application.services.course_service.db")
@patch("application.services.course_service.Course")
def test_create(mock_course, mock_db):

    course = MagicMock()

    mock_course.return_value = course

    result = CourseService.create({
        "title": "Python",
        "description": "Curso"
    })

    assert result == course

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


# Actualizar curso existente
@patch("application.services.course_service.db")
@patch("application.services.course_service.Course")
def test_update_existing(mock_course, mock_db):

    course = MagicMock()

    mock_course.query.get.return_value = course

    result = CourseService.update(1, {
        "category": "TI",
        "level": "Basico",
        "price": "120",
        "image": "curso.jpg",
        "certificate_image": "cert.jpg"
    })

    assert result == course
    assert course.image == "curso.jpg"
    assert course.certificate_image == "cert.jpg"

    mock_db.session.commit.assert_called_once()


# Actualizar curso inexistente y crearlo
@patch("application.services.course_service.CourseService.create")
@patch("application.services.course_service.CourseService.get_moodle_course")
@patch("application.services.course_service.Course")
def test_update_create_new_course(
    mock_course,
    mock_get_moodle,
    mock_create
):

    mock_course.query.get.return_value = None
    mock_course.query.filter_by.return_value.first.return_value = None

    mock_get_moodle.return_value = {
        "fullname": "Python Avanzado",
        "summary": "Curso completo"
    }

    created = MagicMock()

    mock_create.return_value = created

    result = CourseService.update(99, {})

    assert result == created


# Eliminar curso existente
@patch("application.services.course_service.db")
@patch("application.services.course_service.Course")
def test_delete_existing(mock_course, mock_db):

    course = MagicMock()

    mock_course.query.get.return_value = course

    result = CourseService.delete(1)

    assert result is True

    mock_db.session.delete.assert_called_once_with(course)
    mock_db.session.commit.assert_called_once()


# Eliminar curso inexistente
@patch("application.services.course_service.Course")
def test_delete_not_found(mock_course):

    mock_course.query.get.return_value = None
    mock_course.query.filter_by.return_value.first.return_value = None

    result = CourseService.delete(1)

    assert result is False