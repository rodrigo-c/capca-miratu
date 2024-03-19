from io import BytesIO

from django.urls import reverse

import segno
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph
from svglib.svglib import svg2rlg

from apps.public_queries.lib.dataclasses import PublicQueryData


class PublicQueryExporter:
    def __init__(self, public_query: PublicQueryData, host: str | None = None):
        self.host = host or "localhost"
        self.query_data = public_query
        relative_url = reverse(
            "public_queries:submit", kwargs={"uuid": public_query.url_code}
        )
        self.submit_link = f"https://{self.host}{relative_url}"
        registerFont(
            TTFont("Open Sans", "./static/fonts/Open Sans/OpenSans-VariableFont.ttf")
        )
        registerFont(
            TTFont("Open Sans Bold", "./static/fonts/Open Sans/OpenSans-Bold.ttf")
        )

    def get_share_pdf(self) -> BytesIO:
        pdf_file = BytesIO()
        width, height = letter
        canvas = Canvas(pdf_file, pagesize=letter)
        self._add_header(canvas=canvas)
        self._add_rect_mark(canvas=canvas)
        query_name_height = self._add_query_title(canvas=canvas)
        self._add_qr(canvas=canvas, query_name_height=query_name_height)
        self._add_times(canvas=canvas)
        self._add_link(canvas=canvas)
        canvas.setTitle(f"Consulta Pública - {self.query_data.url_code}")
        canvas.showPage()
        canvas.save()
        pdf_file.seek(0)
        return pdf_file

    def _add_header(self, canvas) -> None:
        logo_gs = svg2rlg("./static/images/logos/gs.svg")
        width, height = letter
        logo_gs.scale(2, 2)
        renderPDF.draw(logo_gs, canvas, 30, height - 70)
        canvas.drawImage(
            "./static/images/logos/cegir.png",
            width - 140,
            height - 50,
            width=85,
            height=17,
        )
        canvas.setFont("Open Sans", size=15)
        canvas.drawCentredString(int(width / 2), height - 65, "Consulta pública")

    def _add_rect_mark(self, canvas) -> None:
        width, height = letter
        canvas.setStrokeColor("#454546")
        canvas.roundRect(
            50, 100, width=width - 100, height=height - 200, radius=10, stroke=1, fill=0
        )

    def _add_query_title(self, canvas) -> None:
        width, height = letter
        styleSheet = getSampleStyleSheet()
        style = styleSheet["BodyText"]
        style.fontSize = 25
        style.fontName = "Open Sans Bold"
        style.leading = 30
        title = Paragraph(self.query_data.name, style)
        w, h = title.wrap(int(width / 1.6), int(height / 2))
        title.drawOn(
            canvas,
            int(width / 4.5),
            height - h - 130,
        )
        return h

    def _add_times(self, canvas) -> None:
        width, height = letter
        canvas.setFont("Open Sans", size=15)
        if self.query_data.end_at:
            end_at = self.query_data.end_at.strftime("%d/%m/%y")
            canvas.drawCentredString(int(width / 2), 45, f"Fecha término: {end_at}")
        if self.query_data.start_at:
            start_at = self.query_data.start_at.strftime("%d/%m/%y")
            label_height = 45 if not self.query_data.end_at else 65
            canvas.drawCentredString(
                int(width / 2), label_height, f"Fecha inicio: {start_at}"
            )

    def _add_link(self, canvas) -> None:
        canvas.setFont("Open Sans", size=12)
        width, height = letter
        canvas.drawCentredString(
            int(width / 2),
            150,
            f"Link: {self.submit_link}",
        )

    def _add_qr(self, canvas, query_name_height: int) -> None:
        width, height = letter
        qrcode = segno.make(self.submit_link)
        qrimage = BytesIO()
        qrcode.save(qrimage, scale=1, kind="png")
        qrimage.seek(0)
        image = ImageReader(qrimage)
        qr_with, qr_height = 300, 300
        canvas.drawImage(
            image,
            int(width / 2) - int(qr_with / 2),
            height - query_name_height - qr_height - 150,
            width=qr_with,
            height=qr_height,
        )
