from infrastructure.database.postgres import db


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    estimated_duration = db.Column(db.String(50), nullable=False)
    delivery_mode = db.Column(db.String(50), nullable=False)
    additional_info = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default="activo", nullable=False)
    image = db.Column(db.String(255), nullable=False)