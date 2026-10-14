from unittest.mock import patch


# Verifica que la página de contacto cargue correctamente.
def test_contact_page_loads(client):
    response = client.get("/contact/")

    assert response.status_code == 200


# Verifica que un mensaje válido se procese y redireccione correctamente.
@patch("presentation.routes.public.contact_routes.save_contact_message")
def test_contact_post_success(mock_save_contact_message, client):

    response = client.post(
        "/contact/",
        data={
            "name": "Jheyson Perez",
            "email": "jheysonperezramirez6@gmail.com",
            "phone": "905921931",
            "message": "Mensaje de prueba"
        }
    )

    assert response.status_code == 302

    mock_save_contact_message.assert_called_once_with(
        "Jheyson Perez",
        "jheysonperezramirez6@gmail.com",
        "905921931",
        "Mensaje de prueba"
    )


# Verifica que se manejen correctamente los errores durante el envío de mensajes.
@patch("presentation.routes.public.contact_routes.save_contact_message")
def test_contact_post_error(mock_save_contact_message, client):

    mock_save_contact_message.side_effect = Exception("Error de prueba")

    response = client.post(
        "/contact/",
        data={
            "name": "Jheyson Perez",
            "email": "jheysonperezramirez6@gmail.com",
            "phone": "905921931",
            "message": "Mensaje de prueba"
        }
    )

    assert response.status_code == 302