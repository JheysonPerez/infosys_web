from flask import Blueprint, redirect, session, url_for, request
from authlib.integrations.flask_client import OAuth
from uuid import uuid4

from config import Config
from application.services.auth_service import is_authorized_user

auth_bp = Blueprint("auth", __name__)

oauth = OAuth()

google = oauth.register(
    name="google",
    client_id=Config.GOOGLE_CLIENT_ID,
    client_secret=Config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
        "code_challenge_method": "S256", 
    }
)

# RUTA LOGIN GOOGLE
@auth_bp.route("/auth/google")
def login_google():
    session.clear()
    
    state = str(uuid4())
    session['google_oauth_state'] = state
    
    redirect_uri = url_for('auth.google_callback', _external=True)
    
    return google.authorize_redirect(redirect_uri, state=state)

# RUTA CALLBACK GOOGLE
@auth_bp.route("/auth/google/callback")
def google_callback():
    if "error" in request.args:
        error = request.args.get("error")
        error_desc = request.args.get("error_description", "Sin descripción")
        print(f"Google OAuth error: {error} - {error_desc}")
        
        if error == "access_denied":
            return redirect(url_for("home.index"))
        
        return f"Error en autenticación: {error} - {error_desc}", 400

    try:
        token = google.authorize_access_token()
    except Exception as e:
        error_str = str(e)
        print("Error al obtener token:", error_str)
        
        if "mismatching_state" in error_str or "CSRF" in error_str:
            session.clear()
            return redirect(url_for("auth.login_google")) 
        
        return "Error al completar la autenticación con Google", 500

    user_info = token.get("userinfo")
    if not user_info:
        try:
            resp = google.get("userinfo")
            resp.raise_for_status()
            user_info = resp.json()
        except Exception as e:
            print("Error obteniendo userinfo:", str(e))
            return "No se pudo obtener la información del usuario", 500

    email = user_info.get("email")
    if not email:
        return "No se recibió correo electrónico del proveedor", 400

    if not is_authorized_user(email):
        return "Usuario no autorizado", 403

    session["user"] = {
        "email": email,
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
    }

    session["is_admin"] = True
    
    session.pop('google_oauth_state', None)

    return redirect("/admin")

# RUTA LOGOUT
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.index"))