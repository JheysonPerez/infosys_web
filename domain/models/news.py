from infrastructure.database.postgres import db
from datetime import date


class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.Date, default=date.today, nullable=False)
    expires_at = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)