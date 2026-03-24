from infrastructure.database.postgres import db
from datetime import date

class News(db.Model):
    __tablename__ = "news"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.Date, default=date.today)
    expires_at = db.Column(db.Date, nullable=True)
