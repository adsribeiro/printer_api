import requests
import base64
import os

class PrinterGateway:
    """SDK Python Simplificado para Printer API Gateway."""
    
    def __init__(self, base_url="http://localhost:5000", api_key="minha_chave_segura_123"):
        self.base_url = base_url.rstrip("/")
        self.headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}

    def imprimir(self, num_pedido: str, impressora: str, conteudo: str):
        """
        Envia um trabalho de impressão. 
        Detecta automaticamente se o conteúdo é PDF (Base64 ou Caminho), ZPL ou Texto.
        """
        # Se for um caminho de arquivo PDF, converte para Base64 automaticamente
        if conteudo.lower().endswith(".pdf") and os.path.exists(conteudo):
            with open(conteudo, "rb") as f:
                conteudo = base64.b64encode(f.read()).decode("utf-8")
        
        payload = {
            "num_pedido": num_pedido,
            "impressora": impressora,
            "conteudo": conteudo
        }
        
        response = requests.post(f"{self.base_url}/imprimir", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def listar_impressoras(self):
        """Retorna o status atual de todas as impressoras."""
        response = requests.get(f"{self.base_url}/impressoras", headers=self.headers)
        response.raise_for_status()
        return response.json()
