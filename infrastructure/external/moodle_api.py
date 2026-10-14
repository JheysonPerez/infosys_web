import requests
from flask import current_app


class MoodleAPI:

    @staticmethod
    def call(function_name, **params):
        url = f"{current_app.config['MOODLE_URL']}/webservice/rest/server.php"

        payload = {
            "wstoken": current_app.config["MOODLE_TOKEN"],
            "moodlewsrestformat": "json",
            "wsfunction": function_name,
            **params,
        }

        response = requests.post(url, data=payload, timeout=15)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and data.get("exception"):
            raise Exception(data.get("message", "Error en Moodle"))

        return data

    @staticmethod
    def get_site_info():
        return MoodleAPI.call("core_webservice_get_site_info")

    @staticmethod
    def get_courses():
        token = current_app.config["MOODLE_TOKEN"]

        data = MoodleAPI.call(
            "core_course_get_courses_by_field", field="", value=""
        )

        courses = []

        for course in data.get("courses", []):
            if course.get("format") == "site":
                continue

            raw_image_url = None
            overviewfiles = course.get("overviewfiles", [])

            if overviewfiles:
                for f in overviewfiles:
                    if f.get("fileurl"):
                        raw_image_url = f.get("fileurl")
                        break

            if not raw_image_url:
                raw_image_url = course.get("courseimage")

            if raw_image_url:
                separator = "&" if "?" in raw_image_url else "?"
                course["courseimage"] = f"{raw_image_url}{separator}token={token}"

            courses.append(course)

        return courses

    @staticmethod
    def get_users(search=""):
        return MoodleAPI.call(
            "core_user_get_users",
            criteria=[{"key": "firstname", "value": search}],
        )

    @staticmethod
    def get_course(course_id):
        courses = MoodleAPI.get_courses()

        for course in courses:
            if int(course["id"]) == int(course_id):
                return {"courses": [course]}

        return {"courses": []}