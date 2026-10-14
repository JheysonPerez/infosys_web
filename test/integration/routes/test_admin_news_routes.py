from unittest.mock import patch, MagicMock


# Verifica que la lista de noticias cargue correctamente.
@patch("presentation.routes.private.admin_news_routes.render_template")
@patch("presentation.routes.private.admin_news_routes.NewsService.get_all")
def test_list_news(
    mock_get_all,
    mock_render,
    admin_client
):

    mock_get_all.return_value = []
    mock_render.return_value = "OK"

    response = admin_client.get("/admin/news/")

    assert response.status_code == 200

    mock_get_all.assert_called_once()
    mock_render.assert_called_once()
    

# Verifica que el formulario de creación de noticias cargue correctamente.
def test_create_news_get(admin_client):

    response = admin_client.get("/admin/news/create")

    assert response.status_code == 200


# Verifica que se cree una noticia correctamente.
@patch("presentation.routes.private.admin_news_routes.save_image")
@patch("presentation.routes.private.admin_news_routes.NewsService.create")
def test_create_news_post(
    mock_create,
    mock_save_image,
    admin_client
):

    mock_save_image.return_value = "imagen.jpg"

    response = admin_client.post(
        "/admin/news/create",
        data={
            "title": "Noticia",
            "content": "Contenido",
            "featured": "on"
        }
    )

    assert response.status_code == 302

    mock_create.assert_called_once()


# Verifica que se muestre el formulario de edición de una noticia existente.
@patch("presentation.routes.private.admin_news_routes.NewsService.get_by_id")
def test_edit_news_get(
    mock_get_by_id,
    admin_client
):

    mock_get_by_id.return_value = MagicMock()

    response = admin_client.get("/admin/news/edit/1")

    assert response.status_code == 200


# Verifica que se redireccione cuando la noticia no existe.
@patch("presentation.routes.private.admin_news_routes.NewsService.get_by_id")
def test_edit_news_not_found(
    mock_get_by_id,
    admin_client
):

    mock_get_by_id.return_value = None

    response = admin_client.get("/admin/news/edit/999")

    assert response.status_code == 302


# Verifica que se actualice una noticia correctamente.
@patch("presentation.routes.private.admin_news_routes.save_image")
@patch("presentation.routes.private.admin_news_routes.NewsService.update")
@patch("presentation.routes.private.admin_news_routes.NewsService.get_by_id")
def test_edit_news_post(
    mock_get_by_id,
    mock_update,
    mock_save_image,
    admin_client
):

    mock_get_by_id.return_value = MagicMock()
    mock_save_image.return_value = "imagen.jpg"

    response = admin_client.post(
        "/admin/news/edit/1",
        data={
            "title": "Editada",
            "content": "Contenido"
        }
    )

    assert response.status_code == 302

    mock_update.assert_called_once()


# Verifica que se elimine una noticia correctamente.
@patch("presentation.routes.private.admin_news_routes.NewsService.delete")
def test_delete_news(
    mock_delete,
    admin_client
):

    response = admin_client.post("/admin/news/delete/1")

    assert response.status_code == 302

    mock_delete.assert_called_once_with(1)