from unittest.mock import MagicMock, patch
from application.services.service_service import ServiceService


# Verifica que se obtengan todos los servicios
@patch("application.services.service_service.Service")
def test_get_all(mock_service):

    expected = [MagicMock(), MagicMock()]

    mock_service.query.all.return_value = expected

    result = ServiceService.get_all()

    assert result == expected


# Verifica que se obtengan únicamente los servicios activos
@patch("application.services.service_service.Service")
def test_get_active(mock_service):

    expected = [MagicMock()]

    mock_service.query.filter_by.return_value.all.return_value = expected

    result = ServiceService.get_active()

    assert result == expected


# Verifica que se obtenga un servicio por su ID
@patch("application.services.service_service.Service")
def test_get_by_id(mock_service):

    service = MagicMock()

    mock_service.query.get.return_value = service

    result = ServiceService.get_by_id(1)

    assert result == service


# Verifica que el filtro de servicios retorne resultados
@patch("application.services.service_service.Service")
def test_filter_services(mock_service):

    expected = [MagicMock()]

    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = expected

    mock_service.query = query_mock

    result = ServiceService.filter_services(
        search="Curso",
        service_type="Capacitacion",
        modality="Virtual",
        duration="20"
    )

    assert result == expected

# Verifica que se obtengan los tipos de servicio disponibles
@patch("application.services.service_service.db")
def test_get_service_types(mock_db):

    mock_db.session.query.return_value.distinct.return_value.all.return_value = [
        ("Capacitacion",),
        ("Consultoria",),
        ("Asesoria",)
    ]

    result = ServiceService.get_service_types()

    assert result == ["Capacitacion", "Consultoria", "Asesoria"]


# Verifica que se obtengan las modalidades disponibles
@patch("application.services.service_service.db")
def test_get_modalities(mock_db):

    mock_db.session.query.return_value.distinct.return_value.all.return_value = [
        ("Virtual",),
        ("Presencial",),
        ("Hibrida",)
    ]

    result = ServiceService.get_modalities()

    assert result == ["Virtual", "Presencial", "Hibrida"]


# Verifica que se generen correctamente los rangos de duración
def test_get_duration_ranges():

    s1 = MagicMock(estimated_duration="10 horas")
    s2 = MagicMock(estimated_duration="20 horas")
    s3 = MagicMock(estimated_duration="10 horas")

    result = ServiceService.get_duration_ranges([s1, s2, s3])

    assert result == ["10 horas", "20 horas"]


# Verifica que se cree correctamente un servicio
@patch("application.services.service_service.db")
@patch("application.services.service_service.Service")
def test_create_service(mock_service, mock_db):

    data = {
        "name": "Servicio Consultoria",
        "description": "Consultoria personalizada",
        "service_type": "Consultoria",
        "estimated_duration": "20 horas",
        "delivery_mode": "Virtual",
        "additional_info": "Con expertos en la materia",
        "price": "100",
        "featured": True,
        "status": "activo",
        "image": "imagen.jpg"
    }

    service = MagicMock()

    mock_service.return_value = service

    result = ServiceService.create(data)

    assert result == service
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


# Verifica que se actualice correctamente un servicio existente
@patch("application.services.service_service.db")
@patch("application.services.service_service.Service")
def test_update_service(mock_service, mock_db):

    service = MagicMock()

    mock_service.query.get.return_value = service

    data = {
        "name": "Actualizado Asesoria",
        "description": "Asesoria personalizada actualizada",
        "service_type": "Asesoria",
        "estimated_duration": "30 horas",
        "delivery_mode": "Presencial",
        "additional_info": "Con expertos en la materia actualizados",
        "price": "200",
        "featured": True,
        "status": "activo",
        "image": "imagen2.jpg"
    }

    result = ServiceService.update(1, data)

    assert result == service
    assert service.image == "imagen2.jpg"
    mock_db.session.commit.assert_called_once()


# Verifica que retorne None al actualizar un servicio inexistente
@patch("application.services.service_service.Service")
def test_update_service_not_found(mock_service):

    mock_service.query.get.return_value = None

    result = ServiceService.update(1, {})

    assert result is None


# Verifica que se elimine correctamente un servicio existente
@patch("application.services.service_service.db")
@patch("application.services.service_service.Service")
def test_delete_service(mock_service, mock_db):

    service = MagicMock()

    mock_service.query.get.return_value = service

    result = ServiceService.delete(1)

    assert result is True
    mock_db.session.delete.assert_called_once_with(service)
    mock_db.session.commit.assert_called_once()


# Verifica que retorne False al eliminar un servicio inexistente
@patch("application.services.service_service.Service")
def test_delete_service_not_found(mock_service):

    mock_service.query.get.return_value = None

    result = ServiceService.delete(1)

    assert result is False