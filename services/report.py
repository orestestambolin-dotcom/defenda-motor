from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from app.core.config import settings

def build_report_pdf(case_id: str, summary: dict, timeline: dict, analysis: dict) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h-50, f"{settings.report_brand_name} — Diagnóstico Jurídico")
    c.setFont("Helvetica", 10)
    c.drawString(40, h-70, f"Caso: {case_id} | Gerado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    y = h-110
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Resumo Executivo")
    y -= 18
    c.setFont("Helvetica", 10)
    c.drawString(40, y, summary.get("headline", "Diagnóstico assistido por IA, validado por advogado."))
    y -= 28

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Principais Achados")
    y -= 16
    c.setFont("Helvetica", 10)
    for f in analysis.get("findings", [])[:6]:
        txt = f"- {f.get('statement','')}"
        c.drawString(45, y, txt[:110])
        y -= 14
        if y < 80:
            c.showPage()
            y = h-60

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Aviso")
    y -= 16
    c.setFont("Helvetica", 9)
    c.drawString(40, y, "Relatório elaborado com apoio de inteligência artificial, sob validação e responsabilidade de advogado habilitado.")
    c.save()

    return buffer.getvalue()
