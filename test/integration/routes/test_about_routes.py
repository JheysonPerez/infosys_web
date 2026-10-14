from unittest.mock import patch, MagicMock

# Verifica que la página "Sobre Nosotros" cargue correctamente y procese los miembros del equipo.
@patch("presentation.routes.public.about_routes.TeamService.build_social_links")
@patch("presentation.routes.public.about_routes.TeamService.get_all_active")
def test_about_page_loads(
    mock_get_all_active,
    mock_build_social_links,
    client
):
    member = MagicMock()
    mock_get_all_active.return_value = [member]

    mock_build_social_links.return_value = {
        "facebook": "#",
        "linkedin": "#"
    }

    response = client.get("/about")

    assert response.status_code == 200

    mock_get_all_active.assert_called_once()
    mock_build_social_links.assert_called_once_with(member)