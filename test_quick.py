import requests
import os
from dotenv import load_dotenv

load_dotenv()

def run_test():
    url = 'http://localhost:5000/imprimir'
    headers = {
        'X-Api-Key': os.getenv('API_KEY', 'minha_chave_segura_123'),
        'Content-Type': 'application/json'
    }
    
    # Enviando o nome da impressora com aspas literais
    payload = {
        "num_pedido": "REQ-ASP-001",
        "impressora": '"Microsoft Print to PDF"',
        "conteudo": "Validando Sanitização:\nO nome da impressora foi enviado com aspas e a API deve limpar automaticamente."
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Resposta: {r.json()}")
    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == "__main__":
    run_test()
