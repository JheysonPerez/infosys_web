ADMIN_EMAIL = "jheyson.xcalibur.15@gmail.com"

# Verifica si el email es del administrador
def is_authorized_user(email):
    return email == ADMIN_EMAIL
