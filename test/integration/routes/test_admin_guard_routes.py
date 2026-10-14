from unittest.mock import patch


# Verifica que si NO hay usuario en sesión
def test_admin_required_no_user(client):
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/auth/google" in response.location.lower() or "login" in response.location.lower()


# Verifica que si el usuario existe pero NO es admin
def test_admin_required_not_admin(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "email": "jheysonperezramirez6@gmail.com"  
        }

    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/auth/logout" in response.location.lower() or "logout" in response.location.lower()


# Verifica que usuario admin autorizado pueda acceder
def test_admin_required_valid_admin(admin_client):
    response = admin_client.get("/admin/")
    assert response.status_code == 200


# Verifica con el segundo email admin
def test_admin_required_second_admin_email(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "email": "infoysys@gmail.com"
        }

    response = client.get("/admin/")
    assert response.status_code == 200


# Verifica case insensitive 
def test_admin_required_email_case_insensitive(client):
    with client.session_transaction() as sess:
        sess["user"] = {
            "email": "JHEYSON.XCALIBUR.15@GMAIL.COM"
        }

    response = client.get("/admin/")
    assert response.status_code == 200


# Verifica acceso a otra ruta protegida 
def test_admin_required_stats_route(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits, \
         patch("application.services.statistic_service.StatisticService.courses_stats") as mock_courses, \
         patch("application.services.statistic_service.StatisticService.services_stats") as mock_services:

        mock_visits.return_value = {}
        mock_courses.return_value = []
        mock_services.return_value = []

        response = admin_client.get("/admin/stats")
        assert response.status_code == 200