from functools import wraps
from flask import session, redirect, url_for

ADMIN_EMAIL = "jheyson.xcalibur.15@gmail.com"


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = session.get("user")

        if not user:
            return redirect(url_for("auth.login_google"))

        if user.get("email") != ADMIN_EMAIL:
            return redirect(url_for("auth.logout"))

        return f(*args, **kwargs)

    return decorated_function
