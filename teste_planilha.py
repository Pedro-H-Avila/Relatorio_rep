from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import Table, TableStyle
import io

from datetime import datetime

AZUL = colors.HexColor("#0B2E83")
AZUL_ESCURO = colors.HexColor("#0A235A")
CINZA_LINHA = colors.HexColor("#F4F6FA")

def moeda(v):
    if isinstance(v, str): return v
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X",".")

# --- Função que desenha o rodapé em todas as páginas ---
def rodape_pdf(canvas, doc):
    largura, altura = landscape(letter)

    # Linha de separação
    canvas.setLineWidth(1)
    canvas.line(20, 65, largura - 20, 65)

    # QR no rodapé (esquerda)
    try:
        canvas.drawImage(
            "C:\\Users\\pedro\\Downloads\\mm\\Relatorio_rep-main\\Relatorio_rep-main\\QR_Code_Buskar.png",
            60, 22,
            width=36, height=36,
            preserveAspectRatio=True,
            mask='auto'
        )
    except Exception as e:
        canvas.setFont("Helvetica", 8)
        canvas.drawString(30, 12, f"[QR indisponível: {e}]")

    # Textos do rodapé
    canvas.setFont("Helvetica", 10)
    canvas.drawString(250, 40, "Rua Levindo Lopes, 391 - Funcionários, Belo Horizonte/MG - CEP: 30140-170")

    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(330, 25, "contato@buskar.me / (31) 98475-4237")
    
    
     
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(HexColor("#1F3A54"))  
    link_text = 'www.buskar.me'
    x = largura -750
    y = 10
    canvas.drawString(x, y, link_text)

    largura_texto = canvas.stringWidth(link_text, "Helvetica-Bold", 10)
    canvas.linkURL("https://www.buskar.me", (x, y, x + largura_texto, y + 7 ), relative=0)

    # canvas.setFillColor(colors.HexColor("#1F3A54"))
    # canvas.setFont("Helvetica-Bold", 10)
    # canvas.drawString(largura - 750, 12, "www.buskar.me")
    # canvas.setFillColor(colors.black)

def cabecalho_pdf(canvas, doc, logo_path):
    largura, altura = landscape(letter)

    # Borda arredondada do cabeçalho
    canvas.setStrokeColor(colors.HexColor("#1F3A54"))
    canvas.setLineWidth(2)
    canvas.roundRect(140, altura - 85, largura - 220, 50, 8, stroke=True, fill=False)

    # Logo (esquerda)
    canvas.drawImage(
        logo_path, 50, altura - 85,
        width=60, height=60,
        preserveAspectRatio=True, mask='auto'
    )

    # Título centralizado dentro da borda
    canvas.setFont("Helvetica-Bold", 18)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(largura/2 + 20, altura - 66, "RELATÓRIO DE VIAGENS")
    
def gerar_relatorio_viagens_memoria(saidas, data_inicio, data_fim, parceiro, valor_total, logo_path, contato):
    buffer = io.BytesIO()  # cria um buffer em memória
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    elementos = []
    styles = getSampleStyleSheet()
    elementos.append(Paragraph(f"Relatório de Viagens - {parceiro}", styles["Title"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Período: {data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')}", styles["Normal"]))
    elementos.append(Paragraph(f"Valor Total: R$ {valor_total:,.2f}", styles["Normal"]))

    doc.build(elementos)

    buffer.seek(0)  # volta o ponteiro para o início
    return buffer.getvalue()  # retorna os bytes do PDF


def gerar_relatorio_viagens(saidas, periodo_ini, periodo_fim, parceiro, total, saida_pdf, logo_path):
    
    doc = SimpleDocTemplate(
        saida_pdf,
        pagesize=landscape(letter),
        leftMargin=10, rightMargin=10,
        topMargin=110,
        bottomMargin=60,
    )

    styles = getSampleStyleSheet()
    p_norm = ParagraphStyle("p_norm", parent=styles["Normal"], fontSize=9, leading=11, wordWrap="LTR")
    p_norm_tight = ParagraphStyle("p_norm_tight", parent=p_norm, leading=10, spaceAfter=0, spaceBefore=0)
    p_header = ParagraphStyle("p_header", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=22)
    # NOVO: estilo centralizado para período/parceiro
    p_center = ParagraphStyle("p_center", parent=styles["Normal"], alignment=TA_CENTER, fontSize=11, leading=14)

    story = []

    # --- Bloco centralizado: Período + Parceiro (2 linhas) ---
    story.append(Paragraph(
        f'Período de <b>{periodo_ini.strftime("%d/%m/%Y")}</b> até <b>{periodo_fim.strftime("%d/%m/%Y")}</b><br/>'
        f'Parceiro: <b>{parceiro}</b>',
        p_center
    ))
    story.append(Spacer(0, 8))

    # --- Linha com "Número de viagens" (esquerda) e "Valor Total" (direita) ---
    num_viagens = len(saidas)
    left_cell = Paragraph(f"Número de viagens: <b>{num_viagens}</b>", styles["Normal"])
    right_cell = Paragraph(f"Valor Total: <b>{moeda(total)}</b>",
                           ParagraphStyle("r", parent=styles["Normal"], alignment=TA_RIGHT))

    metrics_tbl = Table([[left_cell, right_cell]],
                        colWidths=[doc.width/2, doc.width/2],
                        hAlign="CENTER")
    metrics_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))
    story.append(metrics_tbl)
    story.append(Spacer(0, 10))

    # --- Tabela principal ---
    CAB = ["LOTE","FINANCIADO","DATA","VEÍCULO","PLACA","ORIGEM","DESTINO","TIPO","VALOR"]
    data = [CAB]

    for r in saidas:
        data.append([
            r["lote"],
            Paragraph(r["financiado"], p_norm_tight),
            r["data"].strftime("%d/%m/%Y"),
            Paragraph(r["veiculo"], p_norm_tight),
            r["placa"],
            Paragraph(r["origem"], p_norm_tight),
            Paragraph(r["destino"], p_norm_tight),
            Paragraph(r["tipo"], p_norm_tight),
            moeda(r["valor"]),
        ])

    colWidths = [50,130,60,140,55,105,105,55,60]
    tbl = Table(data, colWidths=colWidths, repeatRows=1, hAlign="LEFT")

    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), AZUL),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("ALIGN",      (0,0), (-1,0), "CENTER"),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 10),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),

        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,1), (-1,-1), 8),
        ("VALIGN",   (0,1), (-1,-1), "TOP"),

        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,1), (-1,-1), 4),
        ("BOTTOMPADDING",(0,1), (-1,-1), 4),

        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CINZA_LINHA]),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.HexColor("#C7CEDB")),
        ("BOX",       (0,0), (-1,-1), 0.8, AZUL_ESCURO),

        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("ALIGN", (2,1), (2,-1), "CENTER"),
        ("ALIGN", (4,1), (4,-1), "CENTER"),
        ("ALIGN", (8,1), (8,-1), "RIGHT"),
    ]))

    story.append(tbl)

    # rodapé e cabeçalho em todas as páginas
    doc.build(
        story,
        onFirstPage=lambda c,d: (cabecalho_pdf(c, d, logo_path), rodape_pdf(c, d)),
        onLaterPages=lambda c,d: (cabecalho_pdf(c, d, logo_path), rodape_pdf(c, d))
    )

# ===== exemplo de uso =====
if __name__ == "__main__":
    saidas = [
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    {
        "lote": "25_4186",
        "financiado": "MARCELA CHAVES MARCALA DA CRUZ...",
        "data": datetime(2025,4,29),
        "veiculo": "VW - VolksWagen/Fox 1.0 Mi Total Flex 8V 5p",
        "placa": "AVZ9H58",
        "origem": "BELO HORIZONTE/MG",
        "destino": "RIO DE JANEIRO/RJ",
        "tipo": "estadia",
        "valor": 100.0,
    },
    {
        "lote": "26_4187",
        "financiado": "JOÃO DA SILVA",
        "data": datetime(2025,5,2),
        "veiculo": "Fiat/Uno Mille Fire",
        "placa": "BXY1D23",
        "origem": "SÃO PAULO/SP",
        "destino": "CAMPINAS/SP",
        "tipo": "transporte",
        "valor": 200.0,
    },
    ]
    parceiro = "Rocha_Soluções_em_Transporte_de_veículos_LTDA-Betim_MG"

    nome_arquivo = f"relatorio_viagens_{parceiro}.pdf"
    
    soma = 0

    gerar_relatorio_viagens(
        saidas,
        datetime(2025,8,27), datetime(2025,8,27),
        parceiro,
        42650.00,
        nome_arquivo,
        "C:\\Users\\pedro\\Downloads\\mm\\Relatorio_rep-main\\Relatorio_rep-main\\logo.jpeg",
    )
    print(f"Relatório gerado: {nome_arquivo}")


