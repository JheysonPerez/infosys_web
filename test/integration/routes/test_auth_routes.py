from unittest.mock import patch


# Verifica que el login con Google genere una redirección de autenticación.
@patch("presentation.routes.public.auth_routes.google.authorize_redirect")
def test_login_google(mock_authorize_redirect, client):

    mock_authorize_redirect.return_value = "REDIRECT"

    response = client.get("/auth/google")

    assert response.status_code == 200

    mock_authorize_redirect.assert_called_once()


# Verifica que se redireccione al inicio cuando el usuario cancela la autenticación.
def test_google_callback_access_denied(client):

    response = client.get(
        "/auth/google/callback?error=access_denied"
    )

    assert response.status_code == 302


# Verifica que se manejen errores de autenticación distintos a access_denied.
def test_google_callback_generic_error(client):

    response = client.get(
        "/auth/google/callback?error=server_error&error_description=test"
    )

    assert response.status_code == 400


# Verifica que se rechace el acceso cuando el usuario no está autorizado.
@patch("presentation.routes.public.auth_routes.is_authorized_user")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_unauthorized_user(
    mock_authorize_access_token,
    mock_is_authorized_user,
    client
):

    mock_authorize_access_token.return_value = {
        "userinfo": {
            "email": "jheyson.xcalibur.15@gmail.com",
            "name": "Jheyson Perez",
        }
    }

    mock_is_authorized_user.return_value = False

    response = client.get("/auth/google/callback")

    assert response.status_code == 403


# Verifica que un usuario autorizado inicie sesión correctamente.
@patch("presentation.routes.public.auth_routes.is_authorized_user")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_success(
    mock_authorize_access_token,
    mock_is_authorized_user,
    client
):

    mock_authorize_access_token.return_value = {
        "userinfo": {
            "email": "jheyson.xcalibur.15@gmail.com",
            "name": "Jheyson Perez",
            "picture": "img.jpg"
        }
    }

    mock_is_authorized_user.return_value = True

    response = client.get("/auth/google/callback")

    assert response.status_code == 302

    with client.session_transaction() as sess:
        assert sess["is_admin"] is True
        assert sess["user"]["email"] == "jheyson.xcalibur.15@gmail.com"


# Verifica que se manejen errores CSRF o estados inválidos durante la autenticación.
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_mismatching_state(
    mock_authorize_access_token,
    client
):

    mock_authorize_access_token.side_effect = Exception("mismatching_state")

    response = client.get("/auth/google/callback")

    assert response.status_code == 302


# Verifica que se manejen errores inesperados al obtener el token.
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_token_error(
    mock_authorize_access_token,
    client
):

    mock_authorize_access_token.side_effect = Exception("error cualquiera")

    response = client.get("/auth/google/callback")

    assert response.status_code == 500


# Verifica que se manejen errores al obtener la información del usuario desde Google.
@patch("presentation.routes.public.auth_routes.google.get")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_userinfo_error(
    mock_authorize_access_token,
    mock_google_get,
    client
):

    mock_authorize_access_token.return_value = {}

    mock_google_get.side_effect = Exception("userinfo error")

    response = client.get("/auth/google/callback")

    assert response.status_code == 500


# Verifica que se rechace la autenticación cuando no se recibe un correo electrónico.
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_without_email(
    mock_authorize_access_token,
    client
):

    mock_authorize_access_token.return_value = {
        "userinfo": {
            "name": "Usuario"
        }
    }

    response = client.get("/auth/google/callback")

    assert response.status_code == 400


# Verifica que el cierre de sesión elimine los datos de la sesión.
def test_logout(client):

    with client.session_transaction() as sess:
        sess["is_admin"] = True
        sess["user"] = {"email": "jheyson.xcalibur.15@gmail.com"}

    response = client.get("/logout")

    assert response.status_code == 302

    with client.session_transaction() as sess:
        assert "user" not in sess
        assert "is_admin" not in sess