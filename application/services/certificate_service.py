import os
import qrcode
import uuid
from PIL import Image, ImageDraw, ImageFont
from flask import current_app

from domain.models.certificate import Certificate
from domain.models.course import Course
from infrastructure.database.postgres import db
from application.services.course_service import CourseService


def load_code_font():
    try:
        font_path = os.path.join(
            current_app.root_path,
            "static",
            "fonts",
            "DejaVuSans-Bold.ttf"
        )
        return ImageFont.truetype(font_path, 12)
    except:
        return ImageFont.load_default()


def generate_certificate_image(cert):
    template_name = os.path.basename(
        getattr(cert, "template_snapshot", getattr(cert.course, "certificate_image", "default.png"))
    )
    template_path = os.path.join(
        current_app.root_path,
        "static",
        "images",
        "certificates",
        template_name
    )

    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)

    def load_font(size):
        try:
            font_path = os.path.join(
                current_app.root_path,
                "static",
                "fonts",
                "DejaVuSans-Bold.ttf"
            )
            return ImageFont.truetype(font_path, size)
        except:
            return ImageFont.load_default()

    title_font = load_font(50)
    subtitle_font = load_font(28)
    body_font = load_font(18)

    def fit_text(text, max_width, start_size=50, min_size=25):
        size = start_size
        while size >= min_size:
            font = load_font(size)
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                return font
            size -= 2
        return load_font(min_size)

    name_font = fit_text(cert.student_name, 600, 45, 25)

    def center_text(text, y, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        x = (image.width - width) / 2
        draw.text((x, y), text, fill="black", font=font)

    def left_text(text, x, y, font):
        draw.text((x, y), text, fill="black", font=font)

    def draw_paragraph_justified(draw, text, x, y, font, max_width):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
        if current_line:
            lines.append(current_line)

        line_height = draw.textbbox((0, 0), "Ay", font=font)[3]

        for i, line_words in enumerate(lines):
            line_text = " ".join(line_words)
            if i == len(lines) - 1:
                draw.text((x, y + i * (line_height + 5)), line_text, fill="black", font=font)
                continue
            words_width = sum(draw.textbbox((0, 0), word, font=font)[2] for word in line_words)
            spaces = len(line_words) - 1
            space_width = (max_width - words_width) / spaces if spaces > 0 else 0
            current_x = x
            for word in line_words:
                draw.text((current_x, y + i * (line_height + 5)), word, fill="black", font=font)
                word_width = draw.textbbox((0, 0), word, font=font)[2]
                current_x += word_width + space_width

    def format_rango_fechas(inicio, fin):
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"del {inicio.day} de {meses[inicio.month - 1]} al {fin.day} de {meses[fin.month - 1]}"

    def formatear_fecha(fecha):
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"{fecha.day} de {meses[fecha.month - 1]} de {fecha.year}"

    center_text("CERTIFICADO", 150, title_font)
    x_base = 100
    body_width = 800

    left_text("Otorgado a:", x_base, 220, subtitle_font)
    center_text(cert.student_name, 260, name_font)

    syllabus_text = getattr(cert, "syllabus_snapshot", getattr(cert.course, "syllabus", "Contenido no disponible"))
    syllabus_lines = syllabus_text.splitlines()
    syllabus_font = load_code_font()

    x_syllabus = x_base
    y_syllabus = 570
    line_spacing = 15

    draw.text((x_syllabus, y_syllabus), "Contenido del curso:", fill="black", font=syllabus_font)
    y_syllabus += line_spacing

    for line in syllabus_lines:
        draw.text((x_syllabus, y_syllabus), f"- {line}", fill="black", font=syllabus_font)
        y_syllabus += line_spacing

    texto_completo = (
        f"Por haber culminado y aprobado satisfactoriamente el Curso de Capacitación: "
        f"{cert.course_name}. "
        f"Evento organizado por la empresa Info & Sys Corporation, "
        f"realizado {format_rango_fechas(cert.start_date, cert.end_date)} del presente año, "
        f"con una duración de {cert.duration} horas académicas."
    )

    draw_paragraph_justified(draw, texto_completo, x_base, 330, load_font(18), body_width)

    fecha_texto = f"Tingo María, {formatear_fecha(cert.issue_date)}"
    bbox = draw.textbbox((0, 0), fecha_texto, font=load_font(18))
    text_width = bbox[2] - bbox[0]
    x_fecha = x_base + body_width - text_width
    y_fecha = image.height - 250
    draw.text((x_fecha, y_fecha), fecha_texto, fill="black", font=load_font(18))

    # Código (posición original)
    codigo_texto = cert.code
    bbox = draw.textbbox((0, 0), codigo_texto, font=syllabus_font)
    text_width = bbox[2] - bbox[0]
    x_codigo = x_base + body_width - text_width + 19
    y_codigo = y_fecha + 225
    draw.text((x_codigo, y_codigo), codigo_texto, fill="black", font=syllabus_font)

    # QR
    qr_url = f"https://infosys-web.onrender.com/certificado/{cert.code}"
    qr = qrcode.make(qr_url).resize((90, 90))
    qr_x = image.width - 140
    qr_y = image.height - 127
    image.paste(qr, (qr_x, qr_y))

    return image


def create_certificate(
    student_name,
    student_dni,
    course_id,
    code,
    start_date,
    end_date,
    issue_date,
    type="generated",
    file=None
):
    course = Course.query.get(course_id)
    if not course:
        course = Course.query.filter_by(moodle_course_id=int(course_id)).first()

    if not course:
        raise ValueError("Curso no encontrado")

    course_name = "Curso"
    syllabus = None
    duration = None
    certificate_image = None

    try:
        moodle_course = CourseService.get_moodle_course(course.moodle_course_id)
        if moodle_course:
            course_name = moodle_course.get("fullname", "Curso")
            syllabus = moodle_course.get("syllabus")
            duration = moodle_course.get("estimated_hours")
            certificate_image = moodle_course.get("certificate_image")
    except Exception as e:
        print("Error obteniendo curso Moodle:", e)

    cert = Certificate(
        student_name=student_name,
        student_dni=student_dni,
        course_id=course.id,
        code=code,
        type=type,
        course_name=course_name,
        syllabus_snapshot=syllabus,
        start_date=start_date,
        end_date=end_date,
        issue_date=issue_date,
        duration=duration,
        template_snapshot=certificate_image
    )

    if type == "generated":
        output_folder = os.path.join(current_app.root_path, "static", "images", "generated_certificates")
        os.makedirs(output_folder, exist_ok=True)
        output_filename = f"{code}.png"
        output_path = os.path.join(output_folder, output_filename)

        cert.certificate_image = f"images/generated_certificates/{output_filename}"

        db.session.add(cert)
        db.session.commit()

        image = generate_certificate_image(cert)
        image.save(output_path)
        return cert

    db.session.add(cert)

    if type == "external" and file and file.filename:
        filename = f"{uuid.uuid4().hex}_{file.filename}"

        upload_folder = os.path.join(
            current_app.root_path,
            "static",
            "images",
            "external_certificates"
        )
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, filename)

        image = Image.open(file).convert("RGB")
        draw = ImageDraw.Draw(image)

        # QR
        qr_url = f"https://infosys-web.onrender.com/certificado/{code}"
        qr = qrcode.make(qr_url).resize((90, 90))
        qr_x = image.width - 140
        qr_y = image.height - 127
        image.paste(qr, (qr_x, qr_y))

        font = load_code_font()
        bbox = draw.textbbox((0, 0), code, font=font)
        text_width = bbox[2] - bbox[0]

        x_base = 100
        body_width = 800
        x_codigo = x_base + body_width - text_width + 19
        y_codigo = image.height - 190

        draw.text((x_codigo, y_codigo), code, fill="black", font=font)

        image.save(path, quality=95)
        cert.certificate_image = f"images/external_certificates/{filename}"
        db.session.commit()

        return cert

    else:
        db.session.rollback()
        raise ValueError("Debe subir una imagen para el certificado externo")

    return cert


def search_certificates(query):
    return Certificate.query.filter(
        (Certificate.student_name.ilike(f"%{query}%")) |
        (Certificate.student_dni.ilike(f"%{query}%"))
    ).all()