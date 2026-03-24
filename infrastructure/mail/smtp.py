from flask_mail import Mail, Message

mail = Mail()

def send_email(subject, body, recipients):
    if not recipients:
        return
    msg = Message(subject=subject, recipients=recipients, body=body)
    try:
        mail.send(msg)
    except Exception:
        pass