from application.services.auth_service import is_authorized_user

# Verifica que un correo autorizado retorne True
def test_authorized_user():
    assert is_authorized_user("jheyson.xcalibur.15@gmail.com") is True

# Verifica que la validación no distinga mayúsculas y minúsculas
def test_authorized_user_case_insensitive():
    assert is_authorized_user("JHEYSON.XCALIBUR.15@GMAIL.COM") is True

# Verifica que un correo no autorizado retorne False
def test_unauthorized_user():
    assert is_authorized_user("jheysonperezramirez6@gmail.com") is False