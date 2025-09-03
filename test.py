from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# Função para gerar o relatório
def gerar_comprovante(nome, dados, caminho_pdf_destino):
    c = canvas.Canvas(caminho_pdf_destino, pagesize=letter)
    largura, altura = letter  # Tamanho da página (A4)

    # ===== Bordas arredondadas =====
    c.setStrokeColor(HexColor("#1F3A54"))  # Cor da borda (preto)
    c.setLineWidth(2)  # Espessura da borda
    margem = 27
    largura_caixa = largura - 9 * margem
    altura_caixa = altura - 760
    # x=30, y=60 -> começa um pouco acima do rodapé
    c.roundRect(margem + 115, 686, largura_caixa, altura_caixa, 5, stroke=True, fill=False)

    # ===== Logo =====
    c.drawImage("/home/pedro/Imagens/Imagens Buskar/logo.jpeg", 40, altura - 110, width=65, height=60)
    c.drawImage("/home/pedro/Imagens/Imagens Buskar/logoInter.png", 250, altura - 230, width= 120, height=90)    
    c.drawImage("/home/pedro/Imagens/Imagens Buskar/QR_Code_Buskar.png", 50, altura - 770, width=30, height=30)    


    # ===== Título =====
    c.setFont("Helvetica-Bold", 20)
    c.drawString(160, altura - 96, "COMPROVANTE DE PAGAMENTO")

    # ===== PIX ENVIADO =====
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#000000"))  # Cor laranja
    c.drawString(180, altura - 280, "PIX ENVIADO")

    # Valor
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#000000"))
    c.drawString(310, altura - 279, f"{dados['valor_pix']}")

    # ===== Quem recebeu =====
    c.setFont("Helvetica-Bold", 15)
    c.drawString(20, altura - 340, "Quem recebeu:")
    c.setFont("Helvetica", 12)
    c.drawString(20, altura - 360, f"Nome: {nome}")
    c.drawString(20, altura - 380, f"CPF/CNPJ: {dados['id_recebedor']}")
    c.drawString(20, altura - 400, f"Instituição: {dados['instituicao_recebedor']}")

    # ===== Quem pagou =====
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, altura - 440, "Quem pagou:")
    c.setFont("Helvetica", 12)
    c.drawString(20, altura - 460, f"Nome: {dados['nome_pagador']}")
    c.drawString(20, altura - 480, f"CPF/CNPJ: {dados['id_pagador']}")
    c.drawString(20, altura - 500, f"Instituição: {dados['instituicao_pagador']}")

    # ===== Sobre a transação =====
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20, altura - 540, "Sobre a transação:")
    c.setFont("Helvetica", 12)
    c.drawString(20, altura - 560, f"Data do pagamento: {dados['data_pagamento']}")
    c.drawString(20, altura - 580, f"Horário: {dados['horario_pagamento']}")
    c.drawString(20, altura - 600, f"ID da transação: {dados['id_transacao']}")
    c.drawString(20, altura - 620, f"Descrição: {dados['descricao']}")

    # Linha de separação 
    c.setLineWidth(1) 
    c.line(20, altura - 735, largura - 20, altura - 735)

    # ===== Rodapé =====
    c.setFont("Helvetica", 10)
    c.drawString(150, 40, "Rua Levindo Lopes, 391 - Funcionários, Belo Horizonte/MG - CEP: 30140-170")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(240, 25, "contato@buskar.me / (31) 98475-4237")
    c.setFillColor(HexColor("#1F3A54"))  # Cor laranja
    c.drawString(largura - 580, 10, "www.buskar.me")

    # Salvar o PDF
    c.save()

# ===== Dados de exemplo =====
dados = {
    "valor_pix": "R$ 1.000,00",
    "data_pagamento": "01/09/2025",
    "horario_pagamento": "14:30",
    "id_transacao": "TRANS123456789",
    "descricao": "Pagamento referente à fatura #1234",
    "nome_pagador": "Buskar Logística",
    "id_pagador": "37.131.831/0001-46",
    "instituicao_pagador": "Banco Inter S.A.",
    "id_recebedor": "123.456.789-00",
    "instituicao_recebedor": "Instituição ABC"
}

# Nome do recebedor
nome = "borb"

# Caminho para salvar o PDF
caminho_pdf_destino = "comprovante_borb_reportlab.pdf"

# Gerar o relatório
gerar_comprovante(nome, dados, caminho_pdf_destino)

print(f"Relatório gerado para: {nome}")
