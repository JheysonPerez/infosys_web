import re
from infrastructure.database.postgres import db
from domain.models.team_member import TeamMember

class TeamService:
    # Obtener todos los miembros del equipo
    @staticmethod
    def get_all():
        # Todos los miembros, admin
        return TeamMember.query.order_by(TeamMember.order).all()

    # Obtener solo miembros activos
    @staticmethod
    def get_all_active():
        # Solo miembros activos, vista pública
        return (
            TeamMember.query
            .filter_by(active=True)
            .order_by(TeamMember.order)
            .all()
        )

    # Obtener miembro por ID
    @staticmethod
    def get_by_id(member_id: int):
        return TeamMember.query.get(member_id)

    # Crear nuevo miembro del equipo
    @staticmethod
    def create(data: dict):
        member = TeamMember(
            full_name=data.get("full_name"),
            role=data.get("role"),
            image=data.get("image"),
            instagram=data.get("instagram"),
            facebook=data.get("facebook"),
            whatsapp=data.get("whatsapp"),
            tiktok=data.get("tiktok"),
            order=int(data.get("order") or 0),
            active=True if data.get("active") == "1" else False,  
        )
        db.session.add(member)
        db.session.commit()
        return member

    # Actualizar miembro del equipo
    @staticmethod
    def update(member_id: int, data: dict):
        member = TeamMember.query.get(member_id)
        if not member:
            return None

        member.full_name = data.get("full_name")
        member.role = data.get("role")
        member.image = data.get("image")
        member.instagram = data.get("instagram")
        member.facebook = data.get("facebook")
        member.whatsapp = data.get("whatsapp")
        member.tiktok = data.get("tiktok")
        member.order = int(data.get("order") or 0)
        member.active = True if data.get("active") == "1" else False 

        db.session.commit()
        return member

    # Eliminar miembro del equipo
    @staticmethod
    def delete(member_id: int):
        member = TeamMember.query.get(member_id)
        if not member:
            return False
        db.session.delete(member)
        db.session.commit()
        return True

    # Métodos de redes sociales
    @staticmethod
    def _extract_username(value, platform):
        if not value:
            return None
        value = value.strip()
        patterns = {
            "instagram": r"(?:instagram\.com/)([A-Za-z0-9._]+)",
            "facebook": r"(?:facebook\.com/)([A-Za-z0-9._]+)",
            "tiktok": r"(?:tiktok\.com/@)([A-Za-z0-9._]+)",
            "whatsapp": r"(\d+)",
        }
        match = re.search(patterns.get(platform, ""), value)
        if match:
            return match.group(1)
        return value

    # Construir enlaces completos de redes sociales
    @staticmethod
    def build_social_links(member):
        instagram = TeamService._extract_username(member.instagram, "instagram")
        facebook = TeamService._extract_username(member.facebook, "facebook")
        tiktok = TeamService._extract_username(member.tiktok, "tiktok")
        whatsapp = TeamService._extract_username(member.whatsapp, "whatsapp")
        return {
            "instagram": f"https://www.instagram.com/{instagram}/" if instagram else None,
            "facebook": f"https://www.facebook.com/{facebook}" if facebook else None,
            "tiktok": f"https://www.tiktok.com/@{tiktok}" if tiktok else None,
            "whatsapp": f"https://wa.me/{whatsapp}" if whatsapp else None,
        }