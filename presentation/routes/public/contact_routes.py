from flask import Blueprint, render_template, request, redirect, url_for, flash
from infosys_web.application.services.contact_services import save_contact_message

contact_bp = Blueprint("contact", __name__, url_prefix="/contact") 

# RUTA CONTACTO
@contact_bp.route("/", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone") 
        message = request.form.get("message")

        try:
            save_contact_message(name, email, phone, message)
            flash("Mensaje enviado correctamente", "success")
        except Exception as e:
            print(f"Error guardando o enviando mensaje: {e}")
            flash("Ocurrió un error al enviar el mensaje. Intenta nuevamente.", "danger")
        
        return redirect(url_for("contact.contact"))

    return render_template("contact/contact.html")