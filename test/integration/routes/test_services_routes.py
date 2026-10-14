from unittest.mock import patch, MagicMock


# Verifica que la lista de servicios cargue correctamente.
@patch("presentation.routes.public.services_routes.ServiceService.get_duration_ranges")
@patch("presentation.routes.public.services_routes.ServiceService.get_modalities")
@patch("presentation.routes.public.services_routes.ServiceService.get_service_types")
@patch("presentation.routes.public.services_routes.ServiceService.filter_services")
def test_services_page(
    mock_filter_services,
    mock_get_service_types,
    mock_get_modalities,
    mock_get_duration_ranges,
    client
):

    mock_filter_services.return_value = []
    mock_get_service_types.return_value = []
    mock_get_modalities.return_value = []
    mock_get_duration_ranges.return_value = []

    response = client.get("/services/")

    assert response.status_code == 200


# Verifica que el detalle de un servicio activo cargue correctamente.
@patch("presentation.routes.public.services_routes.StatisticService.register_event")
@patch("presentation.routes.public.services_routes.ServiceService.get_by_id")
def test_service_detail_success(
    mock_get_by_id,
    mock_register_event,
    client
):

    service = MagicMock()
    service.status = "activo"

    mock_get_by_id.return_value = service

    response = client.get("/services/1")

    assert response.status_code == 200

    mock_register_event.assert_called_once_with(
        "service_view",
        1
    )


# Verifica que se retorne 404 cuando el servicio no existe.
@patch("presentation.routes.public.services_routes.ServiceService.get_by_id")
def test_service_detail_not_found(
    mock_get_by_id,
    client
):

    mock_get_by_id.return_value = None

    response = client.get("/services/999")

    assert response.status_code == 404


# Verifica que un servicio inactivo no pueda ser visualizado por usuarios normales.
@patch("presentation.routes.public.services_routes.ServiceService.get_by_id")
def test_service_detail_inactive_service(
    mock_get_by_id,
    client
):

    service = MagicMock()
    service.status = "inactivo"

    mock_get_by_id.return_value = service

    response = client.get("/services/1")

    assert response.status_code == 403


# Verifica que un administrador pueda visualizar servicios inactivos.
@patch("presentation.routes.public.services_routes.StatisticService.register_event")
@patch("presentation.routes.public.services_routes.ServiceService.get_by_id")
def test_service_detail_admin_can_view_inactive(
    mock_get_by_id,
    mock_register_event,
    client
):

    service = MagicMock()
    service.status = "inactivo"

    mock_get_by_id.return_value = service

    with client.session_transaction() as sess:
        sess["is_admin"] = True

    response = client.get("/services/1")

    assert response.status_code == 200

    mock_register_event.assert_called_once_with(
        "service_view",
        1
    )