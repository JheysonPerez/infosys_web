from infrastructure.database.postgres import db
from domain.models.statistic import Statistic
from domain.models.course import Course
from domain.models.services import Service
from sqlalchemy import func
from datetime import datetime, timedelta


class StatisticService:

    @staticmethod
    def register_event(event_type, reference_id=None):
        stat = Statistic(event_type=event_type, reference_id=reference_id)
        db.session.add(stat)
        db.session.commit()

    # RANGO DE FECHAS
    @staticmethod
    def _get_range(mode="range", single_date=None, month=None, start_date=None, end_date=None):
        now = datetime.utcnow()

        try:
            if mode == "day" and single_date:
                start = datetime.strptime(single_date, "%Y-%m-%d")
                end = start

            elif mode == "week" and single_date:
                base = datetime.strptime(single_date, "%Y-%m-%d")
                start = base - timedelta(days=base.weekday()) 
                end = start + timedelta(days=6)

            elif mode == "month" and month:
                year, m = map(int, month.split("-"))
                start = datetime(year, m, 1)

                if m == 12:
                    end = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end = datetime(year, m + 1, 1) - timedelta(days=1)

            else:
                start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else now - timedelta(days=7)
                end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now

        except:
            start = now - timedelta(days=7)
            end = now

        return start, end

    # CURSOS
    @staticmethod
    def courses_stats(order="desc", mode="range", single_date=None, month=None, start_date=None, end_date=None):

        start, end = StatisticService._get_range(mode, single_date, month, start_date, end_date)

        query = db.session.query(
            Course.title,
            func.count().label("total")
        ).select_from(Statistic) \
         .join(Course, Course.id == Statistic.reference_id) \
         .filter(
            Statistic.event_type == "course_view",
            Statistic.created_at >= start,
            Statistic.created_at <= end
        ) \
         .group_by(Course.title)

        if order == "asc":
            query = query.order_by(func.count().asc())
        else:
            query = query.order_by(func.count().desc())

        results = query.all()

        return [(name, max(0, int(total))) for name, total in results]

    # SERVICIOS
    @staticmethod
    def services_stats(order="desc", mode="range", single_date=None, month=None, start_date=None, end_date=None):

        start, end = StatisticService._get_range(mode, single_date, month, start_date, end_date)

        query = db.session.query(
            Service.name,
            func.count().label("total")
        ).select_from(Statistic) \
         .join(Service, Service.id == Statistic.reference_id) \
         .filter(
            Statistic.event_type == "service_view",
            Statistic.created_at >= start,
            Statistic.created_at <= end
        ) \
         .group_by(Service.name)

        if order == "asc":
            query = query.order_by(func.count().asc())
        else:
            query = query.order_by(func.count().desc())

        results = query.all()

        return [(name, max(0, int(total))) for name, total in results]

    # VISITAS
    @staticmethod
    def visits(mode="range", single_date=None, month=None, start_date=None, end_date=None):

        start, end = StatisticService._get_range(mode, single_date, month, start_date, end_date)

        results = db.session.query(
            func.date(Statistic.created_at),
            func.count()
        ).filter(
            Statistic.event_type == "visit",
            Statistic.created_at >= start,
            Statistic.created_at <= end
        ).group_by(
            func.date(Statistic.created_at)
        ).all()

        data_dict = {
            date.strftime("%Y-%m-%d"): int(total)
            for date, total in results
        }

        full_data = []
        current = start

        while current <= end:
            key = current.strftime("%Y-%m-%d")
            label = current.strftime("%d/%m")

            total = max(0, int(data_dict.get(key, 0)))
            full_data.append((label, total))

            current += timedelta(days=1)

        return full_data