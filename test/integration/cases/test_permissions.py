import pytest


# sin login
def test_admin_access_without_login(client):
    response = client.get("/admin")
    assert response.status_code in [302, 303, 308]


# no admin
def test_admin_access_not_admin(client):
    with client.session_transaction() as sess:
        sess["user"] = {"email": "fake@mail.com"}

    response = client.get("/admin")
    assert response.status_code in [302, 303, 308]


# admin permitido
def test_admin_access_allowed(client):
    with client.session_transaction() as sess:
        sess["user"] = {"email": "jheyson.xcalibur.15@gmail.com"}

    response = client.get("/admin")
    assert response.status_code in [200, 302, 303, 308]


# courses
def test_admin_courses_protected(client):
    response = client.get("/admin/courses")
    assert response.status_code in [302, 303, 308]


# news
def test_admin_news_protected(client):
    response = client.get("/admin/news")
    assert response.status_code in [302, 303, 308]


# services
def test_admin_services_protected(client):
    response = client.get("/admin/services")
    assert response.status_code in [302, 303, 308]


# team
def test_admin_team_protected(client):
    response = client.get("/admin/team")
    assert response.status_code in [302, 303, 308]


# certificates (ESTA NO EXISTE)
def test_admin_certificates_protected(client):
    response = client.get("/admin/certificates")
    assert response.status_code in [302, 303, 308, 404]