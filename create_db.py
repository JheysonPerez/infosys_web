from app import app
from infrastructure.database.postgres import db
from domain.models import (
    Course,
    Service,
    ContactMessage,
    News,
    TeamMember
)

with app.app_context():
    print(" Eliminando tablas existentes...")
    db.drop_all()

    print(" Creando nuevas tablas...")
    db.create_all()

    print(" Base de datos recreada correctamente")
