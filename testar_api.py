import requests
import os
import base64
from dotenv import load_dotenv

load_dotenv()

API_URL = f"http://localhost:{os.getenv('PORTA_API', 5000)}"
API_KEY = os.getenv("API_KEY", "minha_chave_segura_123")
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def enviar_impressao(num_pedido, impressora, conteudo):
    # Se o conteúdo for um caminho de arquivo PDF, converte para Base64
    if conteudo.lower().endswith(".pdf") and os.path.exists(conteudo):
        with open(conteudo, "rb") as f:
            conteudo = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "num_pedido": num_pedido,
        "impressora": impressora,
        "conteudo": conteudo
    }

    print(f"\n⏳ Enviando Pedido {num_pedido} para {impressora}...")
    try:
        r = requests.post(f"{API_URL}/imprimir", headers=HEADERS, json=payload)
        if r.status_code == 200:
            print(f"🚀 Sucesso! Detalhes: {r.json()}")
        else:
            print(f"💥 Erro {r.status_code}: {r.text}")
    except Exception as e:
        print(f"💥 Falha na conexão: {e}")

if __name__ == "__main__":
    print("--- TESTE SIMPLIFICADO PRINTER API ---")
    pedido = input("Número do Pedido: ")
    impressora = input("Nome da Impressora (ex: Microsoft Print to PDF): ")
    print("\nDicas de conteúdo: '^XA...' para Zebra, 'C:\\doc.pdf' para PDF, ou qualquer texto.")
    conteudo = input("Conteúdo ou Caminho PDF: ")
    
    enviar_impressao(pedido, impressora, conteudo)
