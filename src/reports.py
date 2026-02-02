from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""PDF report generation utilities.

This module provides helpers to compose a multi-page PDF report
containing KPIs, AI-generated narrative text and embedded Plotly
images. The primary entry point is `create_pdf_report` which returns
an in-memory `BytesIO` buffer with the generated PDF.
"""


# Auxiliar: quebra de linha
def draw_wrapped_text(c, text, x, y, max_width, line_height=14):
    """Draw wrapped paragraph text into a ReportLab canvas.

    The function performs word-level wrapping using the current font
    metrics reported by the canvas. It writes the wrapped lines
    starting at the (x, y) coordinate and returns the vertical space
    consumed (in points). On error it logs and returns None.

    Parameters
    - c (reportlab.pdfgen.canvas.Canvas): target canvas.
    - text (str): paragraph to render.
    - x (float): left text coordinate (points).
    - y (float): starting baseline y coordinate (points).
    - max_width (float): maximum line width (points).
    - line_height (int): line height/leading (points).

    Returns
    - int | None: total height consumed in points, or None on error.
    """
    try:
        text_obj = c.beginText(x, y)
        text_obj.setFont("Helvetica", 12) 
        text_obj.setFillColor(colors.black)
        
        words = text.split()
        line = ""
        lines_written = 0
        
        for word in words:
            if c.stringWidth(line + word, "Helvetica", 12) < max_width:
                line += word + " "
            else:
                text_obj.textLine(line)
                line = word + " "
                lines_written += 1
        text_obj.textLine(line) # escreve última linha
        lines_written += 1
        
        c.drawText(text_obj)
        return lines_written * line_height
    except Exception as e:
        logger.error(f"Error to wrap text: {e}")
        return None
    
# Gerador de relatórios
def create_pdf_report(text_forecast, text_segmentation, kpi_data, fig_forecast_bytes=None, fig_cluster_bytes=None):
    """Create a two-page PDF report containing KPIs, narratives and images.

    The generated report contains:
    - Page 1: Title, generation timestamp, KPI summary and the financial
      forecast section with an optional forecast image and AI narrative.
    - Page 2: Customer segmentation section with an optional cluster image
      and AI narrative, plus a footer.

    Parameters
    - text_forecast (str): AI-generated narrative for the financial forecast.
    - text_segmentation (str): AI-generated narrative for customer
      segmentation insights.
    - kpi_data (dict): mapping of KPI name -> formatted string value.
    - fig_forecast_bytes (bytes | None): PNG bytes for the forecast plot.
    - fig_cluster_bytes (bytes | None): PNG bytes for the cluster plot.

    Returns
    - io.BytesIO | None: in-memory buffer with the PDF content, or None on error.

    Notes
    - The function logs internal errors and returns None when generation fails.
    """
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Cabeçalho
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "Integrated Strategic Report")
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        c.drawString(50, height - 70, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.line(50, height - 80, width - 50, height - 80)
        c.setFillColor(colors.black)

        y = height - 120

        # KPIs
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "1. Executive Summary (KPIs)")
        y -= 25
        c.setFont("Helvetica", 12)
        for key, value in kpi_data.items():
            c.drawString(70, y, f"• {key}: {value}")
            y -= 20

        # Espaço
        y -= 30

        # Seção: Forecast
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.darkblue)
        c.drawString(50, y, "2. Financial Forecast (12 Months)")
        y -= 10
        c.line(50, y, 250, y)

        # Espaço
        y -= 30

        # Imagem: Forecast
        if fig_forecast_bytes:
            try:
                img = ImageReader(io.BytesIO(fig_forecast_bytes))
                c.drawImage(img, 50, y - 220, width=500, height=220)
                y -= 240
            except:  # noqa: E722
                pass

        # Texto: Forecast
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(50, y, "AI Strategic Analysis:")

        # Espaço
        y -= 20

        height_used = draw_wrapped_text(c, text_forecast, 50, y, width - 100)
        y -= (height_used + 20)

        # Página 2
        c.showPage()
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.darkblue)
        c.drawString(50, y, "3. Customer Segmentation Strategy")
        y -= 10
        c.line(50, y, 320, y)
        y -= 30

        # Imagem: Clusters
        if fig_cluster_bytes:
            try:
                img2 = ImageReader(io.BytesIO(fig_cluster_bytes))
                c.drawImage(img2, 50, y - 250, width=500, height=250)
                y -= 270
            except:  # noqa: E722
                pass

        # Texto: Clusters
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        c.drawString(50, y, "AI Behavioral Insights:")
        y -= 20
        draw_wrapped_text(c, text_segmentation, 50, y, width - 100)

        # Rodapé
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)
        c.drawString(50, 30, "Retail Analytics App - Confidential")

        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error to generate PDF report: {e}")
        return None