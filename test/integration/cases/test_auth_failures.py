import pytest
from unittest.mock import patch


# error access denied de google
def test_google_callback_access_denied(client):
    response = client.get("/auth/google/callback?error=access_denied")
    assert response.status_code in [302, 303]


# error generico oauth
def test_google_callback_generic_error(client):
    response = client.get("/auth/google/callback?error=invalid_request&error_description=test")
    assert response.status_code == 400
    assert b"Error en autenticaci" in response.data


# error mismatching state csrf
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_mismatching_state(mock_token, client):
    mock_token.side_effect = Exception("mismatching_state CSRF detected")
    response = client.get("/auth/google/callback")
    assert response.status_code in [302, 303]


# usuario sin email
@patch("presentation.routes.public.auth_routes.google.get")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_no_email(mock_token, mock_get, client):
    mock_token.return_value = {}

    mock_get.return_value.json.return_value = {
        "name": "Test User",
        "picture": "img.png"
        # sin email
    }

    response = client.get("/auth/google/callback")
    assert response.status_code == 400
    assert b"correo electr" in response.data.lower()


# usuario no autorizado
@patch("presentation.routes.public.auth_routes.is_authorized_user")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_user_not_authorized(mock_token, mock_auth, client):
    mock_token.return_value = {
        "userinfo": {
            "email": "fake@mail.com",
            "name": "Fake",
            "picture": ""
        }
    }

    mock_auth.return_value = False

    response = client.get("/auth/google/callback")
    assert response.status_code == 403


# login exitoso
@patch("presentation.routes.public.auth_routes.is_authorized_user")
@patch("presentation.routes.public.auth_routes.google.authorize_access_token")
def test_google_callback_success(mock_token, mock_auth, client):
    mock_token.return_value = {
        "userinfo": {
            "email": "admin@test.com",
            "name": "Admin",
            "picture": "img.png"
        }
    }

    mock_auth.return_value = True

    response = client.get("/auth/google/callback")
    assert response.status_code in [302, 303]


# logout limpia sesion
def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess["user"] = {"email": "test@mail.com"}
        sess["is_admin"] = True

    response = client.get("/logout")
    assert response.status_code in [302, 303]

    with client.session_transaction() as sess:
        assert "user" not in sess
        assert "is_admin" not in sess