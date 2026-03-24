from infosys_web.infrastructure.database.postgres import db

class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(150), nullable=False)

    instagram = db.Column(db.String(100))
    facebook = db.Column(db.String(100))
    whatsapp = db.Column(db.String(20))
    tiktok = db.Column(db.String(100))

    order = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"<TeamMember {self.full_name} - {self.role}>"
