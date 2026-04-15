from domain.models.contact_message import ContactMessage
from infrastructure.database.postgres import db
from infrastructure.mail.smtp import send_email
from flask import current_app
import os
import threading


def send_async_email(app, subject, body, recipients):
    try:
        with app.app_context():
            send_email(subject, body, recipients)
    except Exception as e:
        print("ERROR EN HILO EMAIL:", e)


def send_in_thread(subject, body, recipients):
    threading.Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), subject, body, recipients)
    ).start()


def save_contact_message(name, email, phone, message):
    contact = ContactMessage(
        name=name,
        email=email,
        phone=phone,
        message=message
    )
    db.session.add(contact)
    db.session.commit()

    subject_user = "✅ Hemos recibido tu mensaje | Info & Sys Corporation"

    body_user = (
        f"Hola {name},\n"
        "Gracias por ponerte en contacto con Info & Sys Corporation.\n"
        "Hemos recibido correctamente tu mensaje y uno de nuestros asesores se comunicará contigo a la brevedad posible.\n\n"
        "📌 Resumen de tu mensaje:\n"
        f"{message}\n\n"
        "Atentamente,\n"
        "Equipo de Info & Sys Corporation\n"
        "📧 Soporte: jheyson.xcalibur.15@gmail.com\n"
    )

    send_in_thread(subject_user, body_user, [email])

    admin_email = os.getenv("MAIL_RECEIVER")

    if admin_email:
        subject_admin = f"📩 Nuevo contacto de {name} | Info & Sys"

        body_admin = (
            "🔔 NUEVO MENSAJE DE CONTACTO\n\n"
            f"👤 Nombre: {name}\n"
            f"📧 Correo: {email}\n"
            f"📱 Teléfono: {phone}\n\n"
            "💬 Mensaje:\n"
            f"{message}\n\n"
        )

        send_in_thread(subject_admin, body_admin, [admin_email])