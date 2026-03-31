import uuid
import os

from domain.models.certificate import Certificate
from domain.models.course import Course
from infrastructure.database.postgres import db


def create_certificate(student_name, student_dni, course_id):
    code = str(uuid.uuid4())[:8]

    course = Course.query.get(course_id)

    filename = None
    if course and course.certificate_image:
        filename = os.path.basename(course.certificate_image)

    cert = Certificate(
        student_name=student_name,
        student_dni=student_dni,
        course_id=course_id,
        code=code,
        certificate_image=filename
    )

    db.session.add(cert)
    db.session.commit()

    return cert


def search_certificates(query):
    return Certificate.query.filter(
        (Certificate.student_name.ilike(f"%{query}%")) |
        (Certificate.student_dni.ilike(f"%{query}%"))
    ).all()