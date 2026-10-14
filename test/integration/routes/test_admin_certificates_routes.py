import io
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from contextlib import contextmanager

from presentation.routes.private.admin_certificates_routes import db
from domain.models.certificate import Certificate
from domain.models.course import Course

@contextmanager
def app_context(client):
    with client.application.app_context(): yield

# Verifica búsqueda sin filtros
def test_search_admin_empty(client):
    response = client.get("/admin/certificates/search")
    assert response.status_code == 200

# Verifica búsqueda por código
def test_search_admin_by_code(client):
    cert = SimpleNamespace(id=1, student_name="Jheyson Perez", student_dni="12345678", code="2701-2026-ISC", course=None)
    class FakeQuery:
        def filter(self, *args): return self
        def all(self): return [cert]
    with app_context(client), patch.object(Certificate, "query", FakeQuery()):
        response = client.get("/admin/certificates/search?code=2701-2026-ISC")
    assert response.status_code == 200

# Verifica búsqueda por DNI
def test_search_admin_by_dni(client):
    cert = SimpleNamespace(id=1, student_name="Jheyson Perez", student_dni="72257140", code="2701-2026-ISC", course=None)
    class FakeQuery:
        def filter(self, *args): return self
        def all(self): return [cert]
    with app_context(client), patch.object(Certificate, "query", FakeQuery()):
        response = client.get("/admin/certificates/search?dni=72257140")
    assert response.status_code == 200

# Verifica búsqueda por código y DNI
def test_search_admin_by_code_and_dni(client):
    cert = SimpleNamespace(id=1, student_name="Jheyson Perez", student_dni="72257140", code="2701-2026-ISC", course=None)
    class FakeQuery:
        def filter(self, *args): return self
        def all(self): return [cert]
    with app_context(client), patch.object(Certificate, "query", FakeQuery()):
        response = client.get("/admin/certificates/search?code=2701-2026-ISC&dni=72257140")
    assert response.status_code == 200

# Verifica formulario de nuevo certificado (GET)
def test_new_certificate_get(client):
    class FakeQuery:
        def all(self): return []
    with app_context(client), patch.object(Course, "query", FakeQuery()):
        response = client.get("/admin/certificates/new")
    assert response.status_code == 200

# Verifica creación de certificado (POST)
def test_new_certificate_post(client):
    class FakeQuery:
        def all(self): return []
    with app_context(client), patch.object(Course, "query", FakeQuery()), \
         patch("presentation.routes.private.admin_certificates_routes.create_certificate", return_value=True):
        response = client.post("/admin/certificates/new", data={"student_name": "Jheyson Perez", "student_dni": "72257140", "course_id": "1", "code": "2701-2026-ISC", "start_date": "2026-01-01", "end_date": "2026-01-10"}, follow_redirects=False)
    assert response.status_code == 302

# Verifica formulario de edición (GET)
def test_edit_certificate_get(client):
    cert = SimpleNamespace(id=1, student_name="Jheyson Perez", student_dni="72257140", course_id=1, code="2701-2026-ISC", start_date=None, end_date=None, type="generated")
    class FakeCertQuery:
        def get_or_404(self, cert_id): return cert
    class FakeCourseQuery:
        def all(self): return []
    with app_context(client), patch.object(Certificate, "query", FakeCertQuery()), patch.object(Course, "query", FakeCourseQuery()):
        response = client.get("/admin/certificates/edit/1")
    assert response.status_code == 200

# Verifica actualización de certificado (POST)
def test_edit_certificate_post(client):
    cert = SimpleNamespace(id=1, student_name="Jheyson Perez", student_dni="72257140", course_id=1, code="2701-2026-ISC", start_date=None, end_date=None, type="generated")
    course = SimpleNamespace(title="Curso Test", estimated_hours=40)
    class FakeCertQuery:
        def get_or_404(self, cert_id): return cert
    class FakeCourseQuery:
        def all(self): return []
        def get(self, course_id): return course
    with app_context(client), patch.object(Certificate, "query", FakeCertQuery()), patch.object(Course, "query", FakeCourseQuery()), patch.object(db.session, "commit", return_value=None):
        response = client.post("/admin/certificates/edit/1", data={"student_name": "Jheyson Perez", "student_dni": "72257140", "course_id": "1", "code": "2701-2026-ISC", "start_date": "2026-01-01", "end_date": "2026-01-10", "type": "generated"}, follow_redirects=False)
    assert response.status_code == 302

# Verifica eliminación de certificado
def test_delete_certificate(client):
    cert = SimpleNamespace(id=1)
    class FakeQuery:
        def get_or_404(self, cert_id): return cert
    with app_context(client), patch.object(Certificate, "query", FakeQuery()), patch.object(db.session, "delete", return_value=None), patch.object(db.session, "commit", return_value=None):
        response = client.post("/admin/certificates/delete/1", follow_redirects=False)
    assert response.status_code == 302

# Verifica preview con datos incompletos
def test_preview_certificate_missing_data(client):
    response = client.post("/admin/certificates/preview", data={})
    assert response.status_code == 204

# Verifica preview cuando el curso no existe
def test_preview_certificate_course_not_found(client):
    class FakeQuery:
        def get(self, course_id): return None
    with app_context(client), patch.object(Course, "query", FakeQuery()):
        response = client.post("/admin/certificates/preview", data={"student_name": "Jheyson Perez", "course_id": "1", "start_date": "2026-01-01", "end_date": "2026-01-10"})
    assert response.status_code == 204

# Verifica preview de certificado generado
def test_preview_certificate_generated(client):
    course = SimpleNamespace(id=1, title="Curso", estimated_hours=40, syllabus="Tema 1", certificate_image="cert.png")
    class FakeQuery:
        def get(self, course_id): return course
    
    with app_context(client), \
         patch.object(Course, "query", FakeQuery()), \
         patch("presentation.routes.private.admin_certificates_routes.generate_certificate_image", return_value=Image.new("RGB", (100, 100))), \
         patch("presentation.routes.private.admin_certificates_routes.Certificate") as MockCertificate:
        
        mock_cert = SimpleNamespace(id=999, student_name="Jheyson Perez", course=course)
        MockCertificate.return_value = mock_cert
        
        response = client.post("/admin/certificates/preview", data={
            "student_name": "Jheyson Perez",
            "course_id": "1",
            "code": "2701-2026-ISC",
            "start_date": "2026-01-01",
            "end_date": "2026-01-10",
            "type": "generated"
        })
    
    assert response.status_code == 200
    assert response.mimetype == "image/png"

# Verifica preview externo sin archivo
def test_preview_certificate_external_without_file(client):
    course = SimpleNamespace(id=1, title="Curso", estimated_hours=40)
    class FakeQuery:
        def get(self, course_id): return course
    with app_context(client), patch.object(Course, "query", FakeQuery()):
        response = client.post("/admin/certificates/preview", data={"student_name": "Jheyson Perez", "course_id": "1", "start_date": "2026-01-01", "end_date": "2026-01-10", "type": "external"})
    assert response.status_code == 204

# Verifica preview de certificado externo con archivo
def test_preview_certificate_external(client):
    course = SimpleNamespace(id=1, title="Curso", estimated_hours=40)
    class FakeQuery:
        def get(self, course_id): return course
    image = Image.new("RGB", (1000, 1000))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    with app_context(client), patch.object(Course, "query", FakeQuery()):
        response = client.post("/admin/certificates/preview", data={"student_name": "Jheyson Perez", "course_id": "1", "start_date": "2026-01-01", "end_date": "2026-01-10", "type": "external", "certificate_file": (buffer, "cert.png")}, content_type="multipart/form-data")
    assert response.status_code == 200
    assert response.mimetype == "image/png"