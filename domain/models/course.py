from infrastructure.database.postgres import db

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    moodle_course_id = db.Column(db.Integer, unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    level = db.Column(db.String(50), nullable=True)
    modality = db.Column(db.String(50), nullable=True)
    duration_weeks = db.Column(db.Integer, nullable=True)
    estimated_hours = db.Column(db.Integer, nullable=True)
    instructor = db.Column(db.String(120), nullable=True)
    syllabus = db.Column(db.Text, nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default="activo", nullable=False)
    certificate_image = db.Column(db.String(255), nullable=True)