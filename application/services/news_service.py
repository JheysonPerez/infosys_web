from infrastructure.database.postgres import db
from domain.models.news import News
from datetime import date

# Servicio para manejar noticias
class NewsService:

    # todas las noticias 
    @staticmethod
    def get_all():
        return News.query.order_by(News.published_at.desc()).all()


    # obtener por id
    @staticmethod
    def get_by_id(news_id: int):
        return News.query.get(news_id)


    # solo noticias activas 
    @staticmethod
    def get_active():
        today = date.today()

        return News.query.filter(
            News.published_at <= today,
            (News.expires_at == None) | (News.expires_at >= today)
        ).order_by(News.published_at.desc()).all()


    # noticia destacada SOLO si está activa
    @staticmethod
    def get_featured():
        today = date.today()

        return News.query.filter(
            News.featured == True,
            News.published_at <= today,
            (News.expires_at == None) | (News.expires_at >= today)
        ).order_by(News.published_at.desc()).first()


    # crear noticia
    @staticmethod
    def create(data: dict):
        news = News(
            title=data.get("title"),
            content=data.get("content"),
            published_at=data.get("published_at"),
            expires_at=data.get("expires_at") or None,
            image=data.get("image"),
            featured=data.get("featured", False)
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
        news.featured = data.get("featured", False)

        if data.get("image"):
            news.image = data.get("image")

        db.session.commit()
        return news


    # eliminar manual
    @staticmethod
    def delete(news_id: int):
        news = News.query.get(news_id)
        if not news:
            return False

        db.session.delete(news)
        db.session.commit()
        return True