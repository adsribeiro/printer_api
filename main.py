import os
import logging
from logging.handlers import RotatingFileHandler
import win32print
import win32ui
import win32con
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# 1. Configuração Dinâmica e Logging
load_dotenv()

# Configuração de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PrinterAPI")
handler = RotatingFileHandler("printer_api.log", maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

IMPRESSORA_PADRAO = os.getenv("IMPRESSORA_PADRAO", "Microsoft Print to PDF")
PORTA_API = int(os.getenv("PORTA_API", 5000))

app = FastAPI(title="Printer API - Fase 1")

class ImpressaoRequest(BaseModel):
    tipo: str
    conteudo: str
    impressora: str = None  # Agora permite especificar a impressora na requisição

# 2. Tratamento de Erros Refinado
def verificar_impressora(nome_impressora):
    try:
        # Tenta abrir a impressora para verificar se ela existe/está disponível
        hPrinter = win32print.OpenPrinter(nome_impressora)
        win32print.ClosePrinter(hPrinter)
        return True
    except Exception as e:
        logger.error(f"Impressora '{nome_impressora}' não encontrada ou offline: {e}")
        return False

def imprimir_na_comum(nome_impressora, texto):
    try:
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nome_impressora)
        hdc.StartDoc("Pedido Web")
        hdc.StartPage()

        font = win32ui.CreateFont({"name": "Arial", "height": 40, "weight": 400})
        hdc.SelectObject(font)

        y = 100
        for linha in texto.split("\n"):
            hdc.TextOut(100, y, linha)
            y += 60

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
        logger.info(f"Sucesso: Impressão comum enviada para '{nome_impressora}'")
    except Exception as e:
        logger.error(f"Erro ao imprimir na comum ({nome_impressora}): {e}")
        raise Exception(f"Erro no driver da impressora: {e}")

def imprimir_na_zebra(nome_impressora, zpl_code):
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        job = win32print.StartDocPrinter(hPrinter, 1, ("Etiqueta Zebra", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl_code.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)
        logger.info(f"Sucesso: ZPL enviado para '{nome_impressora}'")
    except Exception as e:
        logger.error(f"Erro ao imprimir na Zebra ({nome_impressora}): {e}")
        raise Exception(f"Erro ao enviar comandos RAW: {e}")

# 3. Listagem de Impressoras (Novo Endpoint)
@app.get("/impressoras")
async def listar_impressoras():
    try:
        # Enumera impressoras locais e de rede
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        lista = [imp[2] for imp in impressoras]
        return {"impressoras": lista}
    except Exception as e:
        logger.error(f"Erro ao listar impressoras: {e}")
        raise HTTPException(status_code=500, detail="Não foi possível listar as impressoras.")

@app.post("/imprimir")
async def imprimir(pedido: ImpressaoRequest):
    # Decide qual impressora usar: a da requisição ou a padrão do .env
    nome_impressora = pedido.impressora if pedido.impressora else IMPRESSORA_PADRAO
    
    logger.info(f"Recebida requisição de impressão: tipo={pedido.tipo}, impressora={nome_impressora}")

    if not verificar_impressora(nome_impressora):
        raise HTTPException(status_code=404, detail=f"Impressora '{nome_impressora}' não encontrada.")

    try:
        if pedido.tipo == "zebra":
            imprimir_na_zebra(nome_impressora, pedido.conteudo)
            return {"status": "Enviado ZPL (RAW)", "impressora": nome_impressora}
        else:
            imprimir_na_comum(nome_impressora, pedido.conteudo)
            return {"status": "Sucesso", "impressora": nome_impressora}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info(f"Iniciando Printer API na porta {PORTA_API}...")
    uvicorn.run(app, host="127.0.0.1", port=PORTA_API)
