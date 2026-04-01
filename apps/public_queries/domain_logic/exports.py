from io import BytesIO

from django.urls import reverse

import segno
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

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
        self.canvas_size = (1322, 1614)

    @property
    def width(self):
        return self.canvas_size[0]

    @property
    def height(self):
        return self.canvas_size[1]

    def get_share_pdf(self) -> BytesIO:
        pdf_file = BytesIO()
        canvas = Canvas(pdf_file, pagesize=self.canvas_size)
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
        canvas.setFont("Open Sans Bold", size=36)
        canvas.drawCentredString(
            int(self.width / 2),
            self.height - 100,
            "Consulta pública",
        )

    def _add_rect_mark(self, canvas) -> None:
        canvas.setStrokeColor("#454546")
        canvas.roundRect(
            100,
            200,
            width=self.width - 200,
            height=self.height - 450,
            radius=20,
            stroke=1,
            fill=0,
        )

    def _add_query_title(self, canvas) -> None:
        styleSheet = getSampleStyleSheet()
        style = styleSheet["BodyText"]
        style.alignment = 1
        style.fontSize = 48
        style.fontName = "Open Sans Bold"
        style.leading = 52
        title = Paragraph(self.query_data.name, style)
        w, h = title.wrap(int(self.width / 1.6), int(self.height / 2))
        title.drawOn(
            canvas,
            int(self.width / 5.1),
            self.height - h - 350,
        )
        return h

    def _add_times(self, canvas) -> None:
        canvas.setFont("Open Sans", size=24)
        if self.query_data.end_at:
            end_at = self.query_data.end_at.strftime("%d/%m/%y")
            canvas.drawCentredString(
                int(self.width / 2), 80, f"Fecha término: {end_at}"
            )
        if self.query_data.start_at:
            start_at = self.query_data.start_at.strftime("%d/%m/%y")
            label_height = 90 if not self.query_data.end_at else 110
            canvas.drawCentredString(
                int(self.width / 2), label_height, f"Fecha inicio: {start_at}"
            )

    def _add_link(self, canvas) -> None:
        canvas.setFont("Open Sans", size=36)
        canvas.drawCentredString(
            int(self.width / 2),
            300,
            f"Link: {self.submit_link}",
        )

    def _add_qr(self, canvas, query_name_height: int) -> None:
        qrcode = segno.make(self.submit_link)
        qrimage = BytesIO()
        qrcode.save(qrimage, scale=1, kind="png")
        qrimage.seek(0)
        image = ImageReader(qrimage)
        qr_with, qr_height = 652, 652
        canvas.drawImage(
            image,
            int(self.width / 2) - int(qr_with / 2),
            self.height - query_name_height - qr_height - 400,
            width=qr_with,
            height=qr_height,
        )
