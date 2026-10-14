import io
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage


# Verifica listado de miembros del equipo
def test_list_team(admin_client):
    with patch("application.services.team_service.TeamService.get_all") as mock_get_all, \
         patch("application.services.team_service.TeamService.build_social_links") as mock_build:

        mock_member = MagicMock()
        mock_member.id = 1
        mock_member.full_name = "Jheyson Perez"
        mock_member.role = "Desarrollador Full Stack"
        mock_member.image = "jheyson.jpg"
        mock_member.instagram = "https://instagram.com/jheyson"
        mock_member.facebook = "https://facebook.com/jheyson"
        mock_member.whatsapp = "https://wa.me/905921931"
        mock_member.tiktok = "https://tiktok.com/@archiegod"

        mock_get_all.return_value = [mock_member]
        mock_build.return_value = {
            "instagram": "@jheyson",
            "facebook": "jheyson",
            "whatsapp": "905921931",
            "tiktok": "archiegod"
        }

        response = admin_client.get("/admin/team/")
        assert response.status_code == 200
        assert b"Jheyson Perez" in response.data or b"Desarrollador" in response.data


# Verifica formulario de creación (GET)
def test_create_member_get(admin_client):
    response = admin_client.get("/admin/team/create")
    assert response.status_code == 200


# Verifica creación de miembro (POST)
def test_create_member_post(admin_client):
    with patch("application.services.team_service.TeamService.create") as mock_create, \
         patch("presentation.routes.private.admin_team_routes.save_image") as mock_save:

        mock_save.return_value = "jheyson.jpg"

        data = {
            "full_name": "Jheyson Perez",
            "role": "CEO & Founder",
            "instagram": "https://instagram.com/jheyson",
            "facebook": "https://facebook.com/jheyson",
            "whatsapp": "https://wa.me/905921931",
            "tiktok": "https://tiktok.com/@archiegod"
        }

        response = admin_client.post("/admin/team/create", data=data)
        assert response.status_code == 302
        mock_create.assert_called_once()


# Verifica formulario de edición (GET)
def test_edit_member_get(admin_client):
    with patch("application.services.team_service.TeamService.get_by_id") as mock_get:
        mock_member = MagicMock()
        mock_member.id = 1
        mock_member.full_name = "Jheyson Perez"
        mock_member.role = "Desarrollador Full Stack"
        mock_get.return_value = mock_member

        response = admin_client.get("/admin/team/edit/1")
        assert response.status_code == 200


# Verifica actualización sin nueva imagen
def test_edit_member_post_no_image(admin_client):
    with patch("application.services.team_service.TeamService.get_by_id") as mock_get, \
         patch("application.services.team_service.TeamService.update") as mock_update:

        mock_member = MagicMock()
        mock_member.id = 1
        mock_member.image = "old.jpg"
        mock_get.return_value = mock_member

        data = {
            "full_name": "Jheyson Perez",
            "role": "Desarrollador Full Stack",
            "instagram": "https://instagram.com/jheyson",
            "facebook": "https://facebook.com/jheyson",
            "whatsapp": "https://wa.me/905921931",
            "tiktok": "https://tiktok.com/@archiegod"
        }

        response = admin_client.post("/admin/team/edit/1", data=data)
        assert response.status_code == 302
        mock_update.assert_called_once()


# Verifica actualización con nueva imagen
def test_edit_member_post_with_image(admin_client):
    with patch("application.services.team_service.TeamService.get_by_id") as mock_get, \
         patch("application.services.team_service.TeamService.update") as mock_update, \
         patch("presentation.routes.private.admin_team_routes.save_image") as mock_save:

        mock_member = MagicMock()
        mock_member.id = 1
        mock_member.image = "old.jpg"
        mock_get.return_value = mock_member
        mock_save.return_value = "new-jheyson.jpg"

        image = FileStorage(
            stream=io.BytesIO(b"fake image data"),
            filename="new.jpg",
            content_type="image/jpeg"
        )

        data = {
            "full_name": "Jheyson Perez",
            "role": "Desarrollador Full Stack",
            "instagram": "https://instagram.com/jheyson",
            "facebook": "https://facebook.com/jheyson",
            "whatsapp": "https://wa.me/905921931",
            "tiktok": "https://tiktok.com/@archiegod"
        }

        response = admin_client.post(
            "/admin/team/edit/1",
            data={**data, "image": image},
            content_type="multipart/form-data"
        )
        assert response.status_code == 302


# Verifica eliminación de miembro
def test_delete_member(admin_client):
    with patch("application.services.team_service.TeamService.get_by_id") as mock_get, \
         patch("application.services.team_service.TeamService.delete") as mock_delete, \
         patch("os.path.exists") as mock_exists, \
         patch("os.remove") as mock_remove:

        mock_member = MagicMock()
        mock_member.id = 1
        mock_member.image = "jheyson.jpg"
        mock_get.return_value = mock_member
        mock_exists.return_value = True

        response = admin_client.post("/admin/team/delete/1")
        assert response.status_code == 302
        mock_delete.assert_called_once_with(1)