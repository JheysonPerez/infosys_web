from functools import wraps
from flask import session, redirect, url_for

ADMIN_EMAILS = [
    "jheyson.xcalibur.15@gmail.com",
    "infoysys@gmail.com"
]


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = session.get("user")

        if not user:
            return redirect(url_for("auth.login_google"))

        email = user.get("email", "").lower()

        if email not in [admin.lower() for admin in ADMIN_EMAILS]:
            return redirect(url_for("auth.logout"))

        return f(*args, **kwargs)

    return decorated_function