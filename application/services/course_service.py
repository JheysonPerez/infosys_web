from domain.models import Course
from infrastructure.database.postgres import db
from infrastructure.external.moodle_api import MoodleAPI


# servicio para manejar cursos
class CourseService:

    # obtener todos los cursos locales (admin)
    @staticmethod
    def get_all():
        return Course.query.all()


    # obtener cursos activos locales
    @staticmethod
    def get_active():
        return Course.query.filter_by(status="activo").all()


    # obtener curso local por id
    @staticmethod
    def get_by_id(course_id: int):
        return Course.query.get(course_id)


    @staticmethod
    def get_moodle_course(course_id):

        try:

            data = MoodleAPI.get_course(course_id)
            mc = data["courses"][0] if data.get("courses") else None

            if not mc:
                return None

            local_data = Course.query.filter_by(
                moodle_course_id=int(mc["id"])
            ).first()

            if local_data:

                mc["price"] = local_data.price
                mc["category"] = (
                    local_data.category
                    if local_data.category
                    else mc.get("categoryname")
                )

                mc["modality"] = local_data.modality
                mc["level"] = local_data.level
                mc["duration_weeks"] = local_data.duration_weeks
                mc["estimated_hours"] = local_data.estimated_hours
                mc["instructor"] = local_data.instructor
                mc["certificate_image"] = local_data.certificate_image
                mc["syllabus"] = local_data.syllabus
                mc["additional_info"] = local_data.additional_info
                mc["featured"] = local_data.featured
                mc["status"] = local_data.status

            else:

                mc["price"] = None

                mc["category"] = (
                    mc.get("categoryname")
                    or "Sin categoría"
                )

                mc["modality"] = None
                mc["level"] = None
                mc["duration_weeks"] = None
                mc["estimated_hours"] = None
                mc["instructor"] = None
                mc["certificate_image"] = None
                mc["syllabus"] = None
                mc["additional_info"] = None
                mc["featured"] = False
                mc["status"] = "activo"

            return mc

        except Exception as e:

            print("Error get_moodle_course:", e)
            import traceback
            traceback.print_exc()

            return None


    @staticmethod
    def get_moodle_courses():

        try:

            moodle_courses = MoodleAPI.get_courses()
            local_courses = Course.query.all()

            local_map = {
                c.moodle_course_id: c
                for c in local_courses
                if c.moodle_course_id
            }

            enriched_courses = []

            for mc in moodle_courses:

                moodle_id = mc["id"]

                local_data = local_map.get(moodle_id)

                if local_data:

                    mc["price"] = local_data.price

                    mc["category"] = (
                        local_data.category
                        if local_data.category
                        else mc.get("categoryname")
                    )

                    mc["level"] = local_data.level
                    mc["modality"] = local_data.modality
                    mc["duration_weeks"] = local_data.duration_weeks
                    mc["estimated_hours"] = local_data.estimated_hours
                    mc["instructor"] = local_data.instructor
                    mc["certificate_image"] = local_data.certificate_image
                    mc["syllabus"] = local_data.syllabus
                    mc["additional_info"] = local_data.additional_info
                    mc["featured"] = local_data.featured
                    mc["status"] = local_data.status

                else:

                    mc["price"] = None

                    mc["category"] = (
                        mc.get("categoryname")
                        or "Sin categoría"
                    )

                    mc["level"] = None
                    mc["modality"] = None
                    mc["duration_weeks"] = None
                    mc["estimated_hours"] = None
                    mc["instructor"] = None
                    mc["certificate_image"] = None
                    mc["syllabus"] = None
                    mc["additional_info"] = None
                    mc["featured"] = False
                    mc["status"] = "activo"

                enriched_courses.append(mc)

            return enriched_courses

        except Exception as e:

            print("Error en get_moodle_courses:", e)
            import traceback
            traceback.print_exc()

            return []
        

    # FILTROS
    @staticmethod
    def filter_courses(
        search=None,
        category=None,
        modality=None,
        level=None,
        duration=None,
        include_inactive=False
    ):

        courses = CourseService.get_moodle_courses()

        filtered = []

        for course in courses:

            if not include_inactive:
                if course.get("status", "activo") != "activo":
                    continue

            # Buscar por nombre
            if search and search.strip():
                if search.lower() not in (
                    course.get("fullname", "").lower()
                ):
                    continue

            # Categoría
            if category:
                if (
                    course.get("category", "").lower()
                    != category.lower()
                ):
                    continue

            # Modalidad
            if modality:
                if (
                    course.get("modality", "").lower()
                    != modality.lower()
                ):
                    continue

            # Nivel
            if level:
                if (
                    course.get("level", "").lower()
                    != level.lower()
                ):
                    continue

            # Duración
            if duration:

                weeks = course.get("duration_weeks")

                if weeks:

                    try:

                        if "-" in duration:
                            start, end = map(int, duration.split("-"))

                            if not (start <= weeks <= end):
                                continue

                        else:

                            if weeks != int(duration):
                                continue

                    except:
                        pass

            filtered.append(course)

        return filtered


    # categorías disponibles
    @staticmethod
    def get_categories():

        categorias = db.session.query(
            Course.category
        ).distinct().all()

        return sorted([
            c[0]
            for c in categorias
            if c[0]
        ])


    # modalidades disponibles
    @staticmethod
    def get_modalities():

        modalidades = db.session.query(
            Course.modality
        ).distinct().all()

        return sorted([
            m[0]
            for m in modalidades
            if m[0]
        ])


    # niveles disponibles
    @staticmethod
    def get_levels():

        niveles = db.session.query(
            Course.level
        ).distinct().all()

        return sorted([
            n[0]
            for n in niveles
            if n[0]
        ])


    # rangos de duración dinámicos
    @staticmethod
    def get_duration_ranges(courses):

        duraciones = []

        for c in courses:

            try:

                semanas = c.get("duration_weeks")

                if semanas:
                    duraciones.append(int(semanas))

            except:
                pass

        return sorted(list(set(duraciones)))


    # crear curso local
    @staticmethod
    def create(data):

        course = Course(
            moodle_course_id=int(data["moodle_course_id"]),
            category=data.get("category"),
            level=data.get("level"),
            modality=data.get("modality"),
            duration_weeks=int(data["duration_weeks"]) if data.get("duration_weeks") else None,
            estimated_hours=int(data["estimated_hours"]) if data.get("estimated_hours") else None,
            instructor=data.get("instructor"),
            syllabus=data.get("syllabus"),
            additional_info=data.get("additional_info"),
            price=float(data["price"]) if data.get("price") else None,
            featured=data.get("featured", False),
            status=data.get("status", "activo"),
            certificate_image=data.get("certificate_image")
        )

        db.session.add(course)
        db.session.commit()

        return course

    # actualizar curso local
    @staticmethod
    def update(course_id, data):

        course = Course.query.get(course_id)

        if not course:
            course = Course.query.filter_by(
                moodle_course_id=int(course_id)
            ).first()

        if not course:
            data["moodle_course_id"] = course_id
            return CourseService.create(data)

        course.category = data.get("category")
        course.level = data.get("level")
        course.modality = data.get("modality")

        course.duration_weeks = (int(data["duration_weeks"]) if data.get("duration_weeks") else None)
        course.estimated_hours = (int(data["estimated_hours"]) if data.get("estimated_hours") else None)

        course.instructor = data.get("instructor")
        course.syllabus = data.get("syllabus")
        course.additional_info = data.get("additional_info")

        course.price = (float(data["price"]) if data.get("price") else None)

        course.featured = data.get("featured", False)
        course.status = data.get("status", "activo")

        if "certificate_image" in data:
            course.certificate_image = data["certificate_image"]

        db.session.commit()

        return course

    # eliminar curso local
    @staticmethod
    def delete(course_id):

        course = Course.query.get(course_id)
        if not course:
            course = Course.query.filter_by(moodle_course_id=int(course_id)).first()

        if not course:
            return False

        db.session.delete(course)
        db.session.commit()

        return True