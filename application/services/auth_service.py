ADMIN_EMAILS = [
    "jheyson.xcalibur.15@gmail.com",
    "infoysys@gmail.com"
]

# Verifica si el email es del administrador
def is_authorized_user(email):
    return email.lower() in [admin.lower() for admin in ADMIN_EMAILS]