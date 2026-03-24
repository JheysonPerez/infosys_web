from domain.models.contact_message import ContactMessage
from infrastructure.database.postgres import db
from infrastructure.mail.smtp import send_email
import os
import threading

def send_async_email(subject, body, recipients):
    try:
        send_email(subject, body, recipients)
    except Exception:
        pass

def save_contact_message(name, email, phone, message):
    contact = ContactMessage(
        name=name,
        email=email,
        phone=phone,
        message=message
    )
    db.session.add(contact)
    db.session.commit()

    subject_user = "Gracias por contactarnos"
    body_user = (
        f"Hola {name},\n\n"
        "Hemos recibido tu mensaje y nos pondremos en contacto contigo pronto.\n\n"
        f"Tu mensaje fue:\n{message}\n\n"
        "Saludos,\nInfo & Sys Corporation"
    )

    threading.Thread(target=send_async_email, args=(subject_user, body_user, [email])).start()

    admin_email = os.getenv("MAIL_RECEIVER")
    if admin_email:
        subject_admin = f"Nuevo mensaje de contacto de {name}"
        body_admin = (
            f"Nombre: {name}\n"
            f"Correo: {email}\n"
            f"Teléfono: {phone}\n"
            f"Mensaje:\n{message}"
        )
        threading.Thread(target=send_async_email, args=(subject_admin, body_admin, [admin_email])).start()