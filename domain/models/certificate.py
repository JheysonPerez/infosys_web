from infrastructure.database.postgres import db
from datetime import datetime
from typing import Optional

class Certificate(db.Model):
    __tablename__ = "certificates"
    __allow_unmapped__ = True

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    student_dni = db.Column(db.String(8), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    code = db.Column(db.String(100), unique=True, nullable=False)

    type = db.Column(db.String(20), default="generated") 

    certificate_image = db.Column(db.String(255))

    course = db.relationship("Course", backref="certificates")
    course_name = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    duration = db.Column(db.Integer)

    syllabus_snapshot: Optional[str] = None
    template_snapshot: Optional[str] = None