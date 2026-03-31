from infrastructure.database.postgres import db

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    level = db.Column(db.String(50))
    modality = db.Column(db.String(50))
    duration_weeks = db.Column(db.Integer)
    estimated_hours = db.Column(db.Integer)
    instructor = db.Column(db.String(120))
    syllabus = db.Column(db.Text)
    additional_info = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="activo")
    image = db.Column(db.String(255))
    certificate_image = db.Column(db.String(255))