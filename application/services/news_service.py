from infosys_web.infrastructure.database.postgres import db
from infosys_web.domain.models.news import News

# Servicio para manejar noticias
class NewsService:
    # obtener todas las noticias ordenadas por fecha de publicación
    @staticmethod
    def get_all():
        return News.query.order_by(News.published_at.desc()).all()
    
    # obtener solo noticias activas no expiradas
    @staticmethod
    def get_by_id(news_id: int):
        return News.query.get(news_id)
    
    # obtener solo noticias activas no expiradas
    @staticmethod
    def create(data: dict):
        news = News(
            title=data.get("title"),
            content=data.get("content"),
            published_at=data.get("published_at"),
            expires_at=data.get("expires_at") or None
        )

        db.session.add(news)
        db.session.commit()
        return news
    
    # actualizar noticia
    @staticmethod
    def update(news_id: int, data: dict):
        news = News.query.get(news_id)
        if not news:
            return None

        news.title = data.get("title")
        news.content = data.get("content")
        news.published_at = data.get("published_at")
        news.expires_at = data.get("expires_at") or None

        db.session.commit()
        return news
    
    # eliminar noticia
    @staticmethod
    def delete(news_id: int):
        news = News.query.get(news_id)
        if not news:
            return False

        db.session.delete(news)
        db.session.commit()
        return True