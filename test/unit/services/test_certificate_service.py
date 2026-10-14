from unittest.mock import MagicMock, patch

from application.services.certificate_service import (
    create_certificate,
    search_certificates
)


# Crear certificado generado correctamente
@patch(
    "application.services.certificate_service.current_app",
    new=MagicMock()
)
@patch("application.services.certificate_service.os.makedirs")
@patch("application.services.certificate_service.generate_certificate_image")
@patch("application.services.certificate_service.Course")
@patch("application.services.certificate_service.Certificate")
@patch("application.services.certificate_service.db")
def test_create_generated_certificate(
    mock_db,
    mock_certificate,
    mock_course,
    mock_generate,
    mock_makedirs
):

    from application.services.certificate_service import current_app

    current_app.root_path = "/tmp"

    course = MagicMock()
    course.title = "Python"
    course.syllabus = "Tema 1"
    course.estimated_hours = 40
    course.certificate_image = "template.png"

    mock_course.query.get.return_value = course

    cert = MagicMock()
    mock_certificate.return_value = cert

    fake_image = MagicMock()
    mock_generate.return_value = fake_image

    result = create_certificate(
        "Jheyson Perez Ramirez",
        "12345678",
        1,
        "CERT001",
        MagicMock(),
        MagicMock()
    )

    assert result == cert

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called()
    fake_image.save.assert_called_once()


# Crear certificado externo
@patch(
    "application.services.certificate_service.current_app",
    new=MagicMock()
)
@patch("application.services.certificate_service.os.makedirs")
@patch("application.services.certificate_service.qrcode")
@patch("application.services.certificate_service.Image")
@patch("application.services.certificate_service.Course")
@patch("application.services.certificate_service.Certificate")
@patch("application.services.certificate_service.db")
def test_create_external_certificate(
    mock_db,
    mock_certificate,
    mock_course,
    mock_image_module,
    mock_qrcode,
    mock_makedirs
):

    from application.services.certificate_service import current_app

    current_app.root_path = "/tmp"

    course = MagicMock()
    course.title = "Python"
    course.syllabus = "Tema 1"
    course.estimated_hours = 40
    course.certificate_image = "template.png"

    mock_course.query.get.return_value = course

    cert = MagicMock()
    mock_certificate.return_value = cert

    uploaded_image = MagicMock()
    uploaded_image.width = 1200
    uploaded_image.height = 800

    mock_image_module.open.return_value.convert.return_value = uploaded_image

    qr = MagicMock()
    qr.resize.return_value = qr

    mock_qrcode.make.return_value = qr

    file = MagicMock()
    file.filename = "certificado.png"

    result = create_certificate(
        "Jheyson Perez Ramirez",
        "12345678",
        1,
        "CERT001",
        MagicMock(),
        MagicMock(),
        type="external",
        file=file
    )

    assert result == cert

    uploaded_image.save.assert_called_once()


# Curso no encontrado
@patch("application.services.certificate_service.Course")
def test_create_certificate_course_not_found(mock_course):

    mock_course.query.get.return_value = None

    try:
        create_certificate(
            "Jheyson Perez Ramirez",
            "12345678",
            1,
            "CERT001",
            MagicMock(),
            MagicMock()
        )
        assert False
    except ValueError as e:
        assert str(e) == "Curso no encontrado"


# Certificado externo sin archivo
@patch("application.services.certificate_service.db")
@patch("application.services.certificate_service.Certificate")
@patch("application.services.certificate_service.Course")
def test_create_external_without_file(
    mock_course,
    mock_certificate,
    mock_db
):

    course = MagicMock()
    course.title = "Python"
    course.syllabus = "Tema 1"
    course.estimated_hours = 40
    course.certificate_image = "template.png"

    mock_course.query.get.return_value = course

    cert = MagicMock()
    mock_certificate.return_value = cert

    result = create_certificate(
        "Jheyson Perez Ramirez",
        "12345678",
        1,
        "CERT001",
        MagicMock(),
        MagicMock(),
        type="external",
        file=None
    )

    assert result == cert

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called()


# Buscar certificados
@patch("application.services.certificate_service.Certificate")
def test_search_certificates(mock_certificate):

    expected = [MagicMock()]

    mock_certificate.query.filter.return_value.all.return_value = expected

    result = search_certificates("Jheyson")

    assert result == expected


# Verifica que se genere correctamente la imagen del certificado con los datos del alumno y el código QR
@patch(
    "application.services.certificate_service.current_app",
    new=MagicMock()
)
@patch("application.services.certificate_service.qrcode")
@patch("application.services.certificate_service.ImageFont")
@patch("application.services.certificate_service.ImageDraw")
@patch("application.services.certificate_service.Image")
def test_generate_certificate_image(
    mock_image,
    mock_draw_module,
    mock_font,
    mock_qrcode
):

    from application.services.certificate_service import (
        current_app,
        generate_certificate_image
    )

    current_app.root_path = "/tmp"

    image = MagicMock()
    image.width = 1200
    image.height = 900

    mock_image.open.return_value = image

    draw = MagicMock()
    mock_draw_module.Draw.return_value = draw

    draw.textbbox.return_value = (0, 0, 100, 20)

    font = MagicMock()
    font.path = "font.ttf"

    mock_font.truetype.return_value = font
    mock_font.load_default.return_value = font

    qr = MagicMock()
    qr.resize.return_value = qr

    mock_qrcode.make.return_value = qr

    course = MagicMock()
    course.certificate_image = "template.png"
    course.syllabus = "Tema 1\nTema 2"

    cert = MagicMock()
    cert.student_name = "Jheyson Perez Ramirez"
    cert.course_name = "Python"
    cert.duration = 40
    cert.code = "CERT001"
    cert.course = course

    from datetime import datetime

    cert.start_date = datetime(2026, 1, 1)
    cert.end_date = datetime(2026, 1, 31)

    result = generate_certificate_image(cert)

    assert result == image