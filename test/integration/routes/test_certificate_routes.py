from unittest.mock import patch, MagicMock


# Verifica que la página cargue sin filtros.
def test_certificate_search_without_filters(client):

    response = client.get("/certificados")

    assert response.status_code == 200


# Verifica la búsqueda de certificados por código.
@patch("presentation.routes.public.certificate_routes.Certificate")
def test_certificate_search_by_code(
    mock_certificate,
    client
):

    mock_certificate.query.filter_by.return_value.all.return_value = []

    response = client.get("/certificados?code=ABC123")

    assert response.status_code == 200

    mock_certificate.query.filter_by.assert_called_once_with(
        code="ABC123"
    )


# Verifica la búsqueda de certificados por DNI.
@patch("presentation.routes.public.certificate_routes.Certificate")
def test_certificate_search_by_dni(
    mock_certificate,
    client
):

    mock_certificate.query.filter_by.return_value.all.return_value = []

    response = client.get("/certificados?dni=12345678")

    assert response.status_code == 200

    mock_certificate.query.filter_by.assert_called_once_with(
        student_dni="12345678"
    )


# Verifica la búsqueda de certificados por código y DNI.
@patch("presentation.routes.public.certificate_routes.Certificate")
def test_certificate_search_by_code_and_dni(
    mock_certificate,
    client
):

    mock_certificate.query.filter_by.return_value.all.return_value = []

    response = client.get(
        "/certificados?code=ABC123&dni=12345678"
    )

    assert response.status_code == 200

    mock_certificate.query.filter_by.assert_called_once_with(
        code="ABC123",
        student_dni="12345678"
    )


# Verifica que un administrador pueda acceder a la búsqueda de certificados.
def test_certificate_search_admin_session(client):

    with client.session_transaction() as sess:
        sess["user"] = {
            "is_admin": True
        }

    response = client.get("/certificados")

    assert response.status_code == 200