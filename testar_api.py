import requests
import json
import os
import time
from dotenv import load_dotenv

# Carrega as configurações do .env
load_dotenv()

API_URL = f"http://localhost:{os.getenv('PORTA_API', 5000)}"
API_KEY = os.getenv("API_KEY", "minha_chave_segura_123")
HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_banner():
    print("="*50)
    print("      AURA PRINTER API - CLIENTE DE TESTE      ")
    print("="*50)
    print(f"Endpoint: {API_URL}")
    print("="*50 + "\n")

def testar_conexao():
    try:
        response = requests.get(f"{API_URL}/impressoras", headers=HEADERS)
        if response.status_code == 200:
            print(f"✅ Conexão OK! Impressoras encontradas: {len(response.json()['impressoras'])}")
            return True
        else:
            print(f"❌ Erro de Autenticação: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar na API: {e}")
        return False

def enviar_impressao(tipo, conteudo, formatacao=None):
    payload = {
        "tipo": tipo,
        "conteudo": conteudo
    }
    if formatacao:
        payload["formatacao"] = formatacao

    print(f"\n⏳ Enviando job tipo '{tipo}'...")
    try:
        response = requests.post(f"{API_URL}/imprimir", headers=HEADERS, json=payload)
        if response.status_code == 200:
            res = response.json()
            print(f"🚀 Sucesso! Job ID: {res['job_id']}")
            print(f"📍 Destino: {res['impressora']}")
        else:
            print(f"💥 Erro na API: {response.text}")
    except Exception as e:
        print(f"💥 Erro na requisição: {e}")

def menu():
    while True:
        limpar_tela()
        imprimir_banner()
        
        print("Escolha uma opção de teste:")
        print("1. [Texto] Impressão Comum (Simples)")
        print("2. [Texto] Impressão Comum (Negrito + Grande)")
        print("3. [Zebra] Etiqueta ZPL (ZPL RAW)")
        print("4. [PDF]   Imprimir Arquivo PDF (Caminho Local)")
        print("5. [List]  Listar Impressoras Disponíveis")
        print("0. Sair")
        
        opcao = input("\nDigite o número: ")

        if opcao == "1":
            texto = input("Digite o texto para imprimir: ")
            enviar_impressao("comum", texto)
        
        elif opcao == "2":
            texto = input("Digite o texto para imprimir em DESTAQUE: ")
            fmt = {"negrito": True, "tamanho": 60}
            enviar_impressao("comum", texto, formatacao=fmt)
        
        elif opcao == "3":
            zpl = "^XA^FO50,50^A0N,50,50^FDETIQUETA DE TESTE AURA^FS^XZ"
            print(f"Enviando ZPL Padrão: {zpl}")
            enviar_impressao("zebra", zpl)
        
        elif opcao == "4":
            caminho = input("Digite o caminho completo do PDF (Ex: C:\\temp\\teste.pdf): ")
            enviar_impressao("pdf", caminho)
        
        elif opcao == "5":
            testar_conexao()
        
        elif opcao == "0":
            print("\nEncerrando teste. Até logo!")
            break
        
        else:
            print("\nOpção inválida.")
        
        input("\nPressione ENTER para continuar...")

if __name__ == "__main__":
    if testar_conexao():
        time.sleep(1)
        menu()
    else:
        print("\nCertifique-se que a API está rodando antes de iniciar o script.")
