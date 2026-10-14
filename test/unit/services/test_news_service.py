from unittest.mock import MagicMock, patch
from application.services.news_service import NewsService


# Verifica que se obtengan todas las noticias ordenadas por fecha
@patch("application.services.news_service.News")
def test_get_all(mock_news):

    expected = [MagicMock(), MagicMock()]

    mock_news.query.order_by.return_value.all.return_value = expected

    result = NewsService.get_all()

    assert result == expected


# Verifica que se obtenga una noticia por su ID
@patch("application.services.news_service.News")
def test_get_by_id(mock_news):

    news = MagicMock()

    mock_news.query.get.return_value = news

    result = NewsService.get_by_id(1)

    assert result == news


# Verifica que se obtengan únicamente las noticias activas
@patch.object(NewsService, "get_active")
def test_get_active(mock_get_active):

    expected = [MagicMock()]

    mock_get_active.return_value = expected

    result = NewsService.get_active()

    assert result == expected


# Verifica que se obtenga la noticia destacada activa
@patch.object(NewsService, "get_featured")
def test_get_featured(mock_get_featured):

    featured_news = MagicMock()

    mock_get_featured.return_value = featured_news

    result = NewsService.get_featured()

    assert result == featured_news


# Verifica que se cree correctamente una noticia
@patch("application.services.news_service.db")
@patch("application.services.news_service.News")
def test_create_news(mock_news, mock_db):

    data = {
        "title": "Nueva noticia",
        "content": "Contenido de prueba",
        "published_at": "2026-06-12",
        "expires_at": None,
        "image": "imagen.jpg",
        "featured": True
    }

    news = MagicMock()

    mock_news.return_value = news

    result = NewsService.create(data)

    assert result == news
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


# Verifica que se actualice correctamente una noticia existente
@patch("application.services.news_service.db")
@patch("application.services.news_service.News")
def test_update_news(mock_news, mock_db):

    news = MagicMock()

    mock_news.query.get.return_value = news

    data = {
        "title": "Noticia actualizada",
        "content": "Nuevo contenido de prueba",
        "published_at": "2026-06-12",
        "expires_at": None,
        "image": "imagen2.jpg",
        "featured": True
    }

    result = NewsService.update(1, data)

    assert result == news
    assert news.image == "imagen2.jpg"
    mock_db.session.commit.assert_called_once()


# Verifica que retorne None cuando la noticia no existe al actualizar
@patch("application.services.news_service.News")
def test_update_news_not_found(mock_news):

    mock_news.query.get.return_value = None

    result = NewsService.update(1, {})

    assert result is None


# Verifica que se elimine correctamente una noticia existente
@patch("application.services.news_service.db")
@patch("application.services.news_service.News")
def test_delete_news(mock_news, mock_db):

    news = MagicMock()

    mock_news.query.get.return_value = news

    result = NewsService.delete(1)

    assert result is True
    mock_db.session.delete.assert_called_once_with(news)
    mock_db.session.commit.assert_called_once()


# Verifica que retorne False cuando la noticia no existe al eliminar
@patch("application.services.news_service.News")
def test_delete_news_not_found(mock_news):

    mock_news.query.get.return_value = None

    result = NewsService.delete(1)

    assert result is False