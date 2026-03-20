import requests
import base64
import os

class PrinterGateway:
    """SDK Python para integração com o Printer API Gateway."""
    
    def __init__(self, base_url="http://localhost:5000", api_key="minha_chave_segura_123"):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }

    def list_printers(self):
        """Retorna a lista de impressoras disponíveis."""
        response = requests.get(f"{self.base_url}/impressoras", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def print_text(self, content, printer_name=None, bold=False, size=40, forcar=False):
        """Imprime texto formatado (GDI)."""
        payload = {
            "tipo": "comum",
            "conteudo": content,
            "impressora": printer_name,
            "formatacao": {"negrito": bold, "tamanho": size},
            "forcar": forcar
        }
        return self._send_print_job(payload)

    def print_zpl(self, zpl_string, printer_name=None, forcar=False):
        """Imprime comandos RAW Zebra (ZPL)."""
        payload = {
            "tipo": "zebra",
            "conteudo": zpl_string,
            "impressora": printer_name,
            "forcar": forcar
        }
        return self._send_print_job(payload)

    def print_pdf(self, pdf_path_or_base64, printer_name=None, forcar=False):
        """Imprime um documento PDF (Base64)."""
        content = pdf_path_or_base64
        
        # Se for um caminho de arquivo, converte para Base64
        if os.path.exists(pdf_path_or_base64):
            with open(pdf_path_or_base64, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
        
        payload = {
            "tipo": "pdf",
            "conteudo": content,
            "impressora": printer_name,
            "forcar": forcar
        }
        return self._send_print_job(payload)

    def _send_print_job(self, payload):
        """Envia o trabalho de impressão para a API."""
        response = requests.post(f"{self.base_url}/imprimir", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
