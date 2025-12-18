from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors

def _draw_title(c: canvas.Canvas, text: str, y: float):
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, text)

def _draw_section(c: canvas.Canvas, title: str, lines: list[str], y: float) -> float:
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawString(2*cm, y, title)
    y -= 0.6*cm

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)

    for line in lines:
        # quebra básica de linha
        for chunk in wrap_text(line, max_chars=110):
            if y < 2.2*cm:
                c.showPage()
                y = 28.5*cm
                c.setFont("Helvetica", 10)
            c.drawString(2*cm, y, f"• {chunk}" if chunk == line else f"  {chunk}")
            y -= 0.5*cm

    y -= 0.4*cm
    return y

def wrap_text(text: str, max_chars: int = 110) -> list[str]:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    out, line = [], []
    for w in words:
        if sum(len(x) for x in line) + len(line) + len(w) <= max_chars:
            line.append(w)
        else:
            out.append(" ".join(line))
            line = [w]
    if line:
        out.append(" ".join(line))
    return out

def build_legal_report_pdf(
    *,
    filename: str,
    analysis: dict,
    case_title: str = "Análise Jurídica com IA",
    office_name: str = "Defenda.AI",
) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # Header (faixa)
    c.setFillColor(colors.HexColor("#0B1220"))
    c.rect(0, height-2.2*cm, width, 2.2*cm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height-1.4*cm, office_name)
    c.setFont("Helvetica", 10)
    c.drawRightString(width-2*cm, height-1.4*cm, datetime.now().strftime("%d/%m/%Y %H:%M"))

    # Título
    y = height - 3.2*cm
    c.setFillColor(colors.black)
    _draw_title(c, case_title, y)
    y -= 0.9*cm

    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, f"Arquivo analisado: {filename}")
    y -= 0.8*cm

    # Caixa de aviso
    c.setFillColor(colors.HexColor("#FEF3C7"))
    c.setStrokeColor(colors.HexColor("#F59E0B"))
    c.rect(2*cm, y-1.2*cm, width-4*cm, 1.2*cm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#92400E"))
    c.setFont("Helvetica", 9)
    c.drawString(
        2.2*cm, y-0.6*cm,
        "Aviso: análise automatizada para apoio técnico. Recomenda-se revisão por advogado."
    )
    y -= 1.8*cm

    # Conteúdo
    resumo = analysis.get("resumo", "")
    tipo = analysis.get("tipo_acao_identificada", "")
    confianca = analysis.get("grau_confianca_0a100", 0)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, f"Tipo identificado: {tipo}  |  Confiança: {confianca}/100")
    y -= 0.8*cm

    y = _draw_section(c, "Resumo", wrap_text(resumo, 120), y)

    y = _draw_section(
        c,
        "Pontos de possível prescrição intercorrente",
        analysis.get("pontos_de_prescricao_intercorrente", []) or ["(nenhum ponto identificado)"],
        y,
    )

    y = _draw_section(
        c,
        "Defesas / nulidades / argumentos úteis",
        analysis.get("pontos_de_nulidade_ou_defesas", []) or ["(nenhum ponto identificado)"],
        y,
    )

    y = _draw_section(
        c,
        "Dados que faltam para fechar o parecer",
        analysis.get("dados_que_faltam", []) or ["(nenhum)"],
        y,
    )

    y = _draw_section(
        c,
        "Checklist de próximos passos",
        analysis.get("checklist_proximos_passos", []) or ["(nenhum)"],
        y,
    )

    # Rodapé
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(
        2*cm, 1.4*cm,
        f"{office_name} • Relatório gerado automaticamente • Documento de apoio técnico"
    )

    c.showPage()
    c.save()
    return buf.getvalue()
