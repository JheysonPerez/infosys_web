import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key_fijo")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://infosys_user:infosys123@localhost:5432/infosys_db?client_encoding=utf8"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    SESSION_COOKIE_NAME = "infosys_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  
    SESSION_COOKIE_SAMESITE = "Lax"
