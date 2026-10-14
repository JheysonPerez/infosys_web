from unittest.mock import MagicMock, patch
from application.services.contact_services import (
    send_async_email,
    send_in_thread,
    save_contact_message
)


# Verifica que send_async_email invoque correctamente el envío de correo
@patch("application.services.contact_services.send_email")
def test_send_async_email(mock_send_email):

    mock_app = MagicMock()

    mock_context = MagicMock()
    mock_context.__enter__.return_value = None
    mock_context.__exit__.return_value = None

    mock_app.app_context.return_value = mock_context

    send_async_email(
        mock_app,
        "Mensaje de contacto",
        "Hola mensaje de prueba",
        ["jheysonperezramirez6@gmail.com"]
    )

    mock_send_email.assert_called_once_with(
        "Mensaje de contacto",
        "Hola mensaje de prueba",
        ["jheysonperezramirez6@gmail.com"]
    )


# Verifica que send_in_thread cree e inicie un hilo
@patch("application.services.contact_services.threading.Thread")
@patch("application.services.contact_services.current_app", new=MagicMock())
def test_send_in_thread(mock_thread):

    from application.services.contact_services import current_app

    current_app._get_current_object.return_value = MagicMock()

    send_in_thread(
        "Mensaje de contacto",
        "Hola mensaje de prueba",
        ["jheysonperezramirez6@gmail.com"]
    )

    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()


# Verifica que se guarde el mensaje y se envíe correo al usuario y administrador
@patch("application.services.contact_services.os.getenv")
@patch("application.services.contact_services.send_in_thread")
@patch("application.services.contact_services.db")
@patch("application.services.contact_services.ContactMessage")
def test_save_contact_message(
    mock_contact_message,
    mock_db,
    mock_send_in_thread,
    mock_getenv
):

    mock_getenv.return_value = "jheyson.xcalibur.15@gmail.com"

    save_contact_message(
        "Jheyson Perez Ramirez",
        "jheysonperezramirez6@gmail.com",
        "905921931",
        "Hola mensaje de prueba"
    )

    mock_contact_message.assert_called_once()

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()

    assert mock_send_in_thread.call_count == 2


# Verifica que el sistema intente enviar ambos correos incluso si el email del usuario está vacío
@patch("application.services.contact_services.os.getenv")
@patch("application.services.contact_services.send_in_thread")
@patch("application.services.contact_services.db")
@patch("application.services.contact_services.ContactMessage")
def test_save_contact_message_without_user_email(
    mock_contact_message,
    mock_db,
    mock_send_in_thread,
    mock_getenv
):

    mock_getenv.return_value = "jheyson.xcalibur.15@gmail.com"

    save_contact_message(
        "Jheyson Perez Ramirez",
        "",
        "905921931",
        "Hola mensaje de prueba"
    )

    mock_contact_message.assert_called_once()

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()

    assert mock_send_in_thread.call_count == 1