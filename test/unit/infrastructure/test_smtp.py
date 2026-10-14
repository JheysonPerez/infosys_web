import pytest
from unittest.mock import patch
from flask import Flask

from infrastructure.mail.smtp import send_email, mail


@pytest.fixture
def app():
    app = Flask(__name__)

    app.config["MAIL_DEFAULT_SENDER"] = "jheyson.xcalibur.15@gmail.com"

    mail.init_app(app)

    return app


# Verifica que se llame al envío de correo
@patch("infrastructure.mail.smtp.mail.send")
def test_send_email_success(mock_send, app):

    with app.app_context():

        send_email(
            subject="Asunto prueba",
            body="Mensaje prueba",
            recipients=["jheysonperezramirez6@gmail.com"]
        )

        mock_send.assert_called_once()


# Verifica que no se envíe correo sin destinatarios
@patch("infrastructure.mail.smtp.mail.send")
def test_send_email_without_recipients(mock_send):

    send_email(
        subject="Asunto",
        body="Mensaje",
        recipients=[]
    )

    mock_send.assert_not_called()


# Verifica que el envío maneje excepciones correctamente
@patch("infrastructure.mail.smtp.mail.send")
def test_send_email_exception(mock_send, app):

    mock_send.side_effect = Exception("SMTP Error")

    with app.app_context():

        send_email(
            subject="Asunto",
            body="Mensaje",
            recipients=["jheysonperezramirez6@gmail.com"]
        )

        mock_send.assert_called_once()