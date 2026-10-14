from unittest.mock import MagicMock, patch
from application.services.team_service import TeamService


# Verifica que se obtengan todos los miembros ordenados
@patch("application.services.team_service.TeamMember")
def test_get_all(mock_team_member):

    expected = [MagicMock(), MagicMock()]

    mock_team_member.query.order_by.return_value.all.return_value = expected

    result = TeamService.get_all()

    assert result == expected


# Verifica que se obtengan solo los miembros activos
@patch("application.services.team_service.TeamMember")
def test_get_all_active(mock_team_member):

    expected = [MagicMock()]

    (
        mock_team_member.query
        .filter_by.return_value
        .order_by.return_value
        .all.return_value
    ) = expected

    result = TeamService.get_all_active()

    assert result == expected


# Verifica que se obtenga un miembro por su ID
@patch("application.services.team_service.TeamMember")
def test_get_by_id(mock_team_member):

    member = MagicMock()

    mock_team_member.query.get.return_value = member

    result = TeamService.get_by_id(1)

    assert result == member


# Verifica que se cree correctamente un miembro del equipo
@patch("application.services.team_service.db")
@patch("application.services.team_service.TeamMember")
def test_create_member(mock_team_member, mock_db):

    data = {
        "full_name": "Jheyson Perez",
        "role": "Practicante PPP",
        "image": "foto.jpg",
        "instagram": "jheyson.15dev",
        "facebook": "jheyson.perez",
        "whatsapp": "905921931",
        "tiktok": "archiegod15",
        "order": "1",
        "active": "1"
    }

    member = MagicMock()
    mock_team_member.return_value = member

    result = TeamService.create(data)

    assert result == member
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


# Verifica que se actualice correctamente un miembro existente
@patch("application.services.team_service.db")
@patch("application.services.team_service.TeamMember")
def test_update_member(mock_team_member, mock_db):

    member = MagicMock()

    mock_team_member.query.get.return_value = member

    data = {
        "full_name": "Jheyson Perez",
        "role": "Practicante PPP",
        "image": "foto.jpg",
        "instagram": "jheyson.15dev",
        "facebook": "jheyson.perez",
        "whatsapp": "905921931",
        "tiktok": "archiegod15",
        "order": "2",
        "active": "1"
    }

    result = TeamService.update(1, data)

    assert result == member
    mock_db.session.commit.assert_called_once()


# Verifica que retorne None cuando el miembro no existe al actualizar
@patch("application.services.team_service.TeamMember")
def test_update_member_not_found(mock_team_member):

    mock_team_member.query.get.return_value = None

    result = TeamService.update(1, {})

    assert result is None


# Verifica que se elimine correctamente un miembro existente
@patch("application.services.team_service.db")
@patch("application.services.team_service.TeamMember")
def test_delete_member(mock_team_member, mock_db):

    member = MagicMock()

    mock_team_member.query.get.return_value = member

    result = TeamService.delete(1)

    assert result is True
    mock_db.session.delete.assert_called_once_with(member)
    mock_db.session.commit.assert_called_once()


# Verifica que retorne False cuando el miembro no existe al eliminar
@patch("application.services.team_service.TeamMember")
def test_delete_member_not_found(mock_team_member):

    mock_team_member.query.get.return_value = None

    result = TeamService.delete(1)

    assert result is False


# Verifica que se extraiga correctamente un usuario de Instagram desde una URL
def test_extract_instagram_username():

    result = TeamService._extract_username(
        "https://instagram.com/jheyson.15dev",
        "instagram"
    )

    assert result == "jheyson.15dev"


# Verifica que se extraiga correctamente un número de WhatsApp
def test_extract_whatsapp_number():

    result = TeamService._extract_username(
        "51905921931",
        "whatsapp"
    )

    assert result == "51905921931"


# Verifica que retorne None cuando no se proporciona valor
def test_extract_username_none():

    result = TeamService._extract_username(None, "instagram")

    assert result is None


# Verifica que se construyan correctamente los enlaces de redes sociales
def test_build_social_links():

    member = MagicMock()

    member.instagram = "https://instagram.com/jheyson.15dev"
    member.facebook = "https://facebook.com/jheyson.perez"
    member.tiktok = "https://tiktok.com/@archiegod15"
    member.whatsapp = "51905921931"

    links = TeamService.build_social_links(member)

    assert links["instagram"] == "https://www.instagram.com/jheyson.15dev/"
    assert links["facebook"] == "https://www.facebook.com/jheyson.perez"
    assert links["tiktok"] == "https://www.tiktok.com/@archiegod15"
    assert links["whatsapp"] == "https://wa.me/51905921931"