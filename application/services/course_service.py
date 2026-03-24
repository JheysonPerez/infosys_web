from infosys_web.domain.models import Course
from infosys_web.infrastructure.database.postgres import db

# servicio para manejar cursos
class CourseService:

    # obtener todos los cursos
    @staticmethod
    def get_all():
        return Course.query.all()

    # obtener solo cursos activos
    @staticmethod
    def get_active():
        return Course.query.filter_by(status="activo").all()

    # obtener curso por id
    @staticmethod
    def get_by_id(course_id: int):
        return Course.query.get(course_id)

    # filtrar cursos
    @staticmethod
    def filter_courses(
        search=None,
        category=None,
        modality=None,
        level=None,
        duration=None,
        include_inactive=False
    ):

        query = Course.query

        # solo activos si no es admin
        if not include_inactive:
            query = query.filter(Course.status == "activo")

        # búsqueda
        if search and search.strip():
            query = query.filter(
                Course.title.ilike(f"%{search.strip()}%")
            )

        # categoría
        if category:
            query = query.filter(
                db.func.lower(Course.category) == category.lower()
            )

        # modalidad
        if modality:
            query = query.filter(
                db.func.lower(Course.modality) == modality.lower()
            )

        # nivel
        if level:
            query = query.filter(
                db.func.lower(Course.level) == level.lower()
            )

        # duración
        if duration:
            try:
                if "-" in duration:
                    start, end = map(int, duration.split("-"))
                    query = query.filter(
                        Course.duration_weeks >= start,
                        Course.duration_weeks <= end
                    )
                else:
                    query = query.filter(
                        Course.duration_weeks == int(duration)
                    )
            except:
                pass

        return query.all()

    # crear curso
    @staticmethod
    def create(data: dict):

        course = Course(
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            level=data.get("level"),
            modality=data.get("modality"),
            duration_weeks=int(data.get("duration_weeks") or 0),
            estimated_hours=int(data.get("estimated_hours") or 0),
            instructor=data.get("instructor"),
            syllabus=data.get("syllabus"),
            additional_info=data.get("additional_info"),

            # FIX PRICE 
            price=float(data.get("price")) if data.get("price") else None,

            # FIX FEATURED
            featured=True if data.get("featured") else False,

            status=data.get("status", "activo"),

            # GUARDAR IMAGEN
            image=data.get("image")
        )

        db.session.add(course)
        db.session.commit()
        return course

    # actualizar curso
    @staticmethod
    def update(course_id: int, data: dict):

        course = Course.query.get(course_id)

        if not course:
            return None

        course.title = data.get("title", course.title)
        course.description = data.get("description", course.description)
        course.category = data.get("category", course.category)
        course.level = data.get("level", course.level)
        course.modality = data.get("modality", course.modality)

        course.duration_weeks = int(data.get("duration_weeks") or course.duration_weeks or 0)
        course.estimated_hours = int(data.get("estimated_hours") or course.estimated_hours or 0)

        course.instructor = data.get("instructor", course.instructor)
        course.syllabus = data.get("syllabus", course.syllabus)
        course.additional_info = data.get("additional_info", course.additional_info)

        # FIX PRICE
        course.price = float(data.get("price")) if data.get("price") else None

        # FIX FEATURED
        course.featured = True if data.get("featured") else False

        course.status = data.get("status", course.status)

        # ACTUALIZAR IMAGEN SOLO SI VIENE NUEVA
        if data.get("image"):
            course.image = data.get("image")

        db.session.commit()
        return course

    # eliminar curso
    @staticmethod
    def delete(course_id: int):

        course = Course.query.get(course_id)

        if not course:
            return False

        db.session.delete(course)
        db.session.commit()
        return True