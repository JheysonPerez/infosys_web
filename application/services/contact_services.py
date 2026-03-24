from infosys_web.domain.models.contact_message import ContactMessage
from infosys_web.infrastructure.database.postgres import db
from infosys_web.infrastructure.mail.smtp import send_email
import os

def save_contact_message(name, email, phone, message):
    # Guardar en la base de datos
    contact = ContactMessage(
        name=name,
        email=email,
        phone=phone,
        message=message
    )
    db.session.add(contact)
    db.session.commit()

    # Correo de confirmación al usuario
    subject_user = "Gracias por contactarnos"
    body_user = (
        f"Hola {name},\n\n"
        "Hemos recibido tu mensaje y nos pondremos en contacto contigo pronto.\n\n"
        f"Tu mensaje fue:\n{message}\n\n"
        "Saludos,\nInfo & Sys Corporation"
    )

    try:
        send_email(subject_user, body_user, [email])
    except Exception:
        # Opcional: aquí puedes registrar el error en logs si quieres
        pass

    # Correo al administrador con todos los datos del formulario
    admin_email = os.getenv("MAIL_RECEIVER")
    if admin_email:
        subject_admin = f"Nuevo mensaje de contacto de {name}"
        body_admin = (
            f"Nombre: {name}\n"
            f"Correo: {email}\n"
            f"Teléfono: {phone}\n"
            f"Mensaje:\n{message}"
        )
        try:
            send_email(subject_admin, body_admin, [admin_email])
        except Exception:
            pass