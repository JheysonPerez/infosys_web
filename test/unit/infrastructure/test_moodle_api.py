from unittest.mock import MagicMock, patch
from flask import Flask

from infrastructure.external.moodle_api import MoodleAPI


# Ejecuta una llamada exitosa a Moodle
@patch("infrastructure.external.moodle_api.requests.post")
def test_call_success(mock_post):

    app = Flask(__name__)

    app.config["MOODLE_URL"] = "https://moodle.test"
    app.config["MOODLE_TOKEN"] = "token"

    response = MagicMock()
    response.json.return_value = {"success": True}

    mock_post.return_value = response

    with app.app_context():

        result = MoodleAPI.call("test_function")

        assert result == {"success": True}

        mock_post.assert_called_once()


# Lanza excepción cuando Moodle devuelve error
@patch("infrastructure.external.moodle_api.requests.post")
def test_call_moodle_exception(mock_post):

    app = Flask(__name__)

    app.config["MOODLE_URL"] = "https://moodle.test"
    app.config["MOODLE_TOKEN"] = "token"

    response = MagicMock()
    response.json.return_value = {
        "exception": "error",
        "message": "Falló Moodle"
    }

    mock_post.return_value = response

    with app.app_context():

        try:
            MoodleAPI.call("test_function")
            assert False
        except Exception as e:
            assert str(e) == "Falló Moodle"


# Obtiene información del sitio
@patch("infrastructure.external.moodle_api.MoodleAPI.call")
def test_get_site_info(mock_call):

    mock_call.return_value = {"site": "InfoSys"}

    result = MoodleAPI.get_site_info()

    assert result == {"site": "InfoSys"}

    mock_call.assert_called_once_with(
        "core_webservice_get_site_info"
    )


# Obtiene lista de cursos
@patch("infrastructure.external.moodle_api.MoodleAPI.call")
def test_get_courses(mock_call):

    mock_call.return_value = [{"id": 1}]

    result = MoodleAPI.get_courses()

    assert result == [{"id": 1}]

    mock_call.assert_called_once_with(
        "core_course_get_courses"
    )


# Busca usuarios por nombre
@patch("infrastructure.external.moodle_api.MoodleAPI.call")
def test_get_users(mock_call):

    MoodleAPI.get_users("Jheyson")

    mock_call.assert_called_once_with(
        "core_user_get_users",
        criteria=[
            {
                "key": "firstname",
                "value": "Jheyson"
            }
        ]
    )


# Obtiene curso por ID
@patch("infrastructure.external.moodle_api.MoodleAPI.call")
def test_get_course(mock_call):

    MoodleAPI.get_course(10)

    mock_call.assert_called_once_with(
        "core_course_get_courses_by_field",
        field="id",
        value=10
    )


# Ejecuta raise_for_status correctamente
@patch("infrastructure.external.moodle_api.requests.post")
def test_call_raise_for_status(mock_post):

    app = Flask(__name__)

    app.config["MOODLE_URL"] = "https://moodle.test"
    app.config["MOODLE_TOKEN"] = "token"

    response = MagicMock()

    mock_post.return_value = response

    with app.app_context():

        MoodleAPI.call("test_function")

        response.raise_for_status.assert_called_once()