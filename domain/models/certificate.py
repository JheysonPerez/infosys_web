from datetime import datetime, UTC
from infrastructure.database.postgres import db

class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    student_name = db.Column(db.String(150), nullable=False)
    student_dni = db.Column(db.String(8), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course_name = db.Column(db.String, nullable=False) 
    duration = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), default="generated", nullable=False)
    certificate_image = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    syllabus_snapshot = db.Column(db.Text, nullable=True)
    template_snapshot = db.Column(db.Text, nullable=True)

    course = db.relationship("Course", backref="certificates")