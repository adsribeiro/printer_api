import requests
import json

BASE_URL = "http://127.0.0.1:5000/imprimir"

def test_impressao_comum():
    payload = {
        "tipo": "comum",
        "conteudo": "Teste de Impressao Comum\nLinha 2\nTotal: R$ 10,00"
    }
    response = requests.post(BASE_URL, json=payload)
    print(f"Teste Comum: {response.status_code} - {response.json()}")

def test_impressao_zebra():
    payload = {
        "tipo": "zebra",
        "conteudo": "^XA^FO50,50^A0N,50,50^FDTeste Zebra^FS^XZ"
    }
    response = requests.post(BASE_URL, json=payload)
    print(f"Teste Zebra: {response.status_code} - {response.json()}")

if __name__ == "__main__":
    try:
        test_impressao_comum()
        test_impressao_zebra()
    except Exception as e:
        print(f"Erro ao testar: {e}")
