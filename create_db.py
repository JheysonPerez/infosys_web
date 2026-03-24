from infosys_web.app import app
from infosys_web.infrastructure.database.postgres import db

from infosys_web.domain.models import (
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
