from flask_mail import Mail, Message

mail = Mail()

def send_email(subject, body, recipients):
    if not recipients:
        return

    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body
    )

    try:
        mail.send(msg)
        print(" Email enviado correctamente a:", recipients)
    except Exception as e:
        print(" ERROR AL ENVIAR EMAIL:", str(e))