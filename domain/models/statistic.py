from infosys_web.infrastructure.database.postgres import db
from datetime import datetime


class Statistic(db.Model):
    __tablename__ = "statistics"

    id = db.Column(db.Integer, primary_key=True)

    # tipo: visit, course_view, service_view
    event_type = db.Column(db.String(50), nullable=False)

    # referencia (id del curso o servicio)
    reference_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)