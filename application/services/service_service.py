from infrastructure.database.postgres import db
from domain.models.services import Service


class ServiceService:
    # Obtener todos los servicios
    @staticmethod
    def get_all():
        return Service.query.all()
    
    # Obtener solo servicios activos
    @staticmethod
    def get_active():
        return Service.query.filter_by(status="activo").all()
    
    # Obtener servicio por ID
    @staticmethod
    def get_by_id(service_id: int):
        return Service.query.get(service_id)

    # FILTROS
    @staticmethod
    def filter_services(
        search=None,
        service_type=None,
        modality=None,
        duration=None,
        include_inactive=False
    ):

        query = Service.query

        if not include_inactive:
            query = query.filter(Service.status == "activo")

        if search and search.strip():
            query = query.filter(
                Service.name.ilike(f"%{search.strip()}%")
            )

        if service_type:
            query = query.filter(
                db.func.lower(Service.service_type) == service_type.lower()
            )

        if modality:
            query = query.filter(
                db.func.lower(Service.delivery_mode) == modality.lower()
            )

        if duration:
            query = query.filter(
                Service.estimated_duration.ilike(f"%{duration}%")
            )

        return query.all()

    # dinámicos
    @staticmethod
    def get_service_types():
        tipos = db.session.query(Service.service_type).distinct().all()
        return [t[0] for t in tipos if t[0]]
    
    # obtener modalidades distintas de los servicios
    @staticmethod
    def get_modalities():
        modalidades = db.session.query(Service.delivery_mode).distinct().all()
        return [m[0] for m in modalidades if m[0]]

    # generar rangos de duración dinámicos
    @staticmethod
    def get_duration_ranges(services):
        duraciones = sorted({
            s.estimated_duration for s in services
            if s.estimated_duration
        })
        return duraciones

    # CREATE 
    @staticmethod
    def create(data: dict):
        service = Service(
            name=data.get("name"),
            description=data.get("description"),
            service_type=data.get("service_type"),
            estimated_duration=data.get("estimated_duration"),
            delivery_mode=data.get("delivery_mode"),
            additional_info=data.get("additional_info"),
            price=float(data.get("price") or 0),
            featured=True if data.get("featured") else False,
            status=data.get("status", "activo"),
            image=data.get("image")
        )

        db.session.add(service)
        db.session.commit()
        return service

    # UPDATE 
    @staticmethod
    def update(service_id: int, data: dict):
        service = Service.query.get(service_id)

        if not service:
            return None

        service.name = data.get("name")
        service.description = data.get("description")
        service.service_type = data.get("service_type")
        service.estimated_duration = data.get("estimated_duration")
        service.delivery_mode = data.get("delivery_mode")
        service.additional_info = data.get("additional_info")
        service.price = float(data.get("price") or 0)
        service.featured = True if data.get("featured") else False
        service.status = data.get("status", "activo")

        if data.get("image"):
            service.image = data.get("image")

        db.session.commit()
        return service

    # DELETE
    @staticmethod
    def delete(service_id: int):
        service = Service.query.get(service_id)

        if not service:
            return False

        db.session.delete(service)
        db.session.commit()
        return True