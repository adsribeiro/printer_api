from printer_client import PrinterGateway

# Configuração
client = PrinterGateway(base_url="http://localhost:5000", api_key="minha_chave_segura_123")

try:
    # 1. Listar impressoras
    printers = client.list_printers()
    print(f"Impressoras encontradas: {len(printers)}")

    # 2. Imprimir texto (GDI)
    print("Enviando teste de texto...")
    res = client.print_text("Olá do SDK Python!\nVersão 5.1", bold=True, size=50)
    print(f"Resposta: {res}")

    # 3. Imprimir PDF (Exemplo com arquivo)
    # res = client.print_pdf("documento.pdf")
    # print(f"PDF enviado: {res}")

except Exception as e:
    print(f"Erro ao integrar: {e}")
