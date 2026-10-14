from unittest.mock import patch


# Verifica que el dashboard admin cargue correctamente
def test_admin_dashboard(admin_client):
    response = admin_client.get("/admin/")
    assert response.status_code == 200
    assert b"panel administrativo" in response.data.lower() or b"dashboard" in response.data.lower()


# Verifica stats con parámetros por defecto
def test_admin_stats_default(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits, \
         patch("application.services.statistic_service.StatisticService.courses_stats") as mock_courses, \
         patch("application.services.statistic_service.StatisticService.services_stats") as mock_services:

        mock_visits.return_value = {"labels": [], "data": []}
        mock_courses.return_value = []
        mock_services.return_value = []

        response = admin_client.get("/admin/stats")
        assert response.status_code == 200


# Verifica stats con rango de fechas
def test_admin_stats_with_date_range(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits, \
         patch("application.services.statistic_service.StatisticService.courses_stats") as mock_courses, \
         patch("application.services.statistic_service.StatisticService.services_stats") as mock_services:

        mock_visits.return_value = {"labels": ["2026-01"], "data": [150]}
        mock_courses.return_value = [{"title": "Python", "count": 45}]
        mock_services.return_value = [{"name": "Certificado", "count": 30}]

        response = admin_client.get("/admin/stats?visits_mode=range&visits_start_date=2026-01-01&visits_end_date=2026-01-31")
        assert response.status_code == 200


# Verifica stats con fecha única
def test_admin_stats_single_date(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits:
        mock_visits.return_value = {"labels": ["2026-01-15"], "data": [89]}

        response = admin_client.get("/admin/stats?visits_mode=single&visits_single_date=2026-01-15")
        assert response.status_code == 200


# Verifica stats por mes
def test_admin_stats_by_month(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits:
        mock_visits.return_value = {"labels": ["Enero"], "data": [420]}

        response = admin_client.get("/admin/stats?visits_mode=month&visits_month=2026-01")
        assert response.status_code == 200


# Verifica respuesta AJAX (JSON)
def test_admin_stats_ajax(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits, \
         patch("application.services.statistic_service.StatisticService.courses_stats") as mock_courses, \
         patch("application.services.statistic_service.StatisticService.services_stats") as mock_services:

        mock_visits.return_value = {"labels": [], "data": []}
        mock_courses.return_value = []
        mock_services.return_value = []

        response = admin_client.get("/admin/stats", headers={"X-Requested-With": "XMLHttpRequest"})

        assert response.status_code == 200
        assert response.is_json


# Verifica filtros de ordenamiento
def test_admin_stats_with_courses_and_services_filters(admin_client):
    with patch("application.services.statistic_service.StatisticService.visits") as mock_visits, \
         patch("application.services.statistic_service.StatisticService.courses_stats") as mock_courses, \
         patch("application.services.statistic_service.StatisticService.services_stats") as mock_services:

        mock_visits.return_value = {}
        mock_courses.return_value = [{"title": "Curso Avanzado", "count": 67}]
        mock_services.return_value = [{"name": "Emisión de Certificado", "count": 23}]

        response = admin_client.get("/admin/stats?courses_order=asc&services_order=desc")
        assert response.status_code == 200