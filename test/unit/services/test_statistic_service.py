from unittest.mock import MagicMock, patch
from application.services.statistic_service import StatisticService
from datetime import datetime


# Verifica que se registre un evento correctamente
@patch("application.services.statistic_service.db")
@patch("application.services.statistic_service.Statistic")
def test_register_event(mock_statistic, mock_db):

    StatisticService.register_event("visit", 1)

    mock_statistic.assert_called_once_with(
        event_type="visit",
        reference_id=1
    )

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


# Verifica que se genere correctamente un rango diario
def test_get_range_day():

    start, end = StatisticService._get_range(
        mode="day",
        single_date="2026-06-01"
    )

    assert start == end
    assert start.year == 2026


# Verifica que se genere correctamente un rango semanal
def test_get_range_week():

    start, end = StatisticService._get_range(
        mode="week",
        single_date="2026-06-03"
    )

    assert (end - start).days == 6


# Verifica que se genere correctamente un rango mensual
def test_get_range_month():

    start, end = StatisticService._get_range(
        mode="month",
        month="2026-06"
    )

    assert start.day == 1
    assert end.day >= 28


# Verifica que una fecha inválida retorne el rango por defecto
def test_get_range_invalid_date():

    start, end = StatisticService._get_range(
        mode="day",
        single_date="fecha-invalida"
    )

    assert start is not None
    assert end is not None


# Verifica que las estadísticas de cursos se obtengan en orden ascendente
@patch("application.services.statistic_service.db")
def test_courses_stats_asc(mock_db):

    query = MagicMock()

    query.select_from.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.order_by.return_value = query

    query.all.return_value = [
        ("Python", 5),
        ("Flask", 10)
    ]

    mock_db.session.query.return_value = query

    result = StatisticService.courses_stats(order="asc")

    assert result == [
        ("Python", 5),
        ("Flask", 10)
    ]


# Verifica que las estadísticas de servicios se obtengan correctamente
@patch("application.services.statistic_service.db")
def test_services_stats_desc(mock_db):

    query = MagicMock()

    query.select_from.return_value = query
    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.order_by.return_value = query

    query.all.return_value = [
        ("Consultoria", 8)
    ]

    mock_db.session.query.return_value = query

    result = StatisticService.services_stats()

    assert result == [
        ("Consultoria", 8)
    ]


# Verifica que las visitas se agrupen correctamente por fecha
@patch("application.services.statistic_service.db")
def test_visits(mock_db):

    query = MagicMock()

    query.filter.return_value = query
    query.group_by.return_value = query

    query.all.return_value = [
        (datetime(2026, 6, 1), 5)
    ]

    mock_db.session.query.return_value = query

    result = StatisticService.visits(
        start_date="2026-06-01",
        end_date="2026-06-01"
    )

    assert result[0][1] == 5