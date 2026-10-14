from unittest.mock import patch


# Verifica que la ruta principal cargue correctamente.
@patch("presentation.routes.public.home_routes.StatisticService.register_event")
@patch("presentation.routes.public.home_routes.render_template")
def test_home_page_loads(
    mock_render,
    mock_register_event,
    client
):
    mock_render.return_value = "HOME"

    response = client.get("/")

    assert response.status_code == 200

    mock_register_event.assert_called_once_with("visit")
    mock_render.assert_called_once()