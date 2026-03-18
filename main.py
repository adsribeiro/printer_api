import os
import logging
import uuid
import sys
from logging.handlers import RotatingFileHandler
import win32print
import win32ui
import win32con
import win32api
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from dotenv import load_dotenv

# 1. Configuração e Logging (UTF-8 Hardened)
load_dotenv()

# Configuração robusta para logs em Windows
log_file = "printer_api.log"
logger = logging.getLogger("PrinterAPI")
logger.setLevel(logging.INFO)

# Remove handlers existentes para evitar duplicidade e conflitos de encoding
if logger.hasHandlers():
    logger.handlers.clear()

# Handler para Arquivo (UTF-8)
file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Handler para Console (UTF-8)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)

# Evitar propagação para o logger raiz que pode estar mal configurado
logger.propagate = False

IMPRESSORA_PADRAO = os.getenv("IMPRESSORA_PADRAO", "Microsoft Print to PDF")
PORTA_API = int(os.getenv("PORTA_API", 5000))
API_KEY = os.getenv("API_KEY", "minha_chave_segura_123")

app = FastAPI(title="Printer API - Gateway Edition")
templates = Jinja2Templates(directory="templates")

# 2. Segurança (API Key)
async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado: Chave de API inválida.")
    return x_api_key

class Formatacao(BaseModel):
    negrito: bool = False
    tamanho: int = 40
    alinhamento: str = "left"

class ImpressaoRequest(BaseModel):
    tipo: str
    conteudo: str
    impressora: Optional[str] = None
    formatacao: Optional[Formatacao] = Formatacao()

def get_printer_status(status_code):
    statuses = {
        0: "Pronta",
        win32print.PRINTER_STATUS_PAUSED: "Pausada",
        win32print.PRINTER_STATUS_ERROR: "Erro",
        win32print.PRINTER_STATUS_OFFLINE: "Offline",
        win32print.PRINTER_STATUS_PAPER_OUT: "Sem Papel",
        win32print.PRINTER_STATUS_PRINTING: "Imprimindo...",
        win32print.PRINTER_STATUS_BUSY: "Ocupada",
    }
    return statuses.get(status_code, f"Status {status_code}")

def get_system_data():
    impressoras_data = []
    try:
        # PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS para pegar tudo
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for imp in impressoras:
            try:
                hPrinter = win32print.OpenPrinter(imp[2])
                info = win32print.GetPrinter(hPrinter, 2)
                impressoras_data.append({
                    "nome": str(imp[2]),
                    "status": get_printer_status(info['Status']),
                    "trabalhos_na_fila": info['cJobs'],
                    "driver": str(info['pDriverName'])
                })
                win32print.ClosePrinter(hPrinter)
            except Exception as e_inner:
                logger.error(f"Erro ao abrir impressora {imp[2]}: {e_inner}")
    except Exception as e:
        logger.error(f"Erro ao listar impressoras: {e}")

    logs = []
    if os.path.exists(log_file):
        try:
            # Lendo com UTF-8 e substituindo caracteres que falharem
            with open(log_file, "r", encoding='utf-8', errors='replace') as f:
                logs = [line.strip() for line in f.readlines()[-25:]]
        except Exception as e:
            logger.error(f"Erro ao ler log: {e}")
    
    return {"impressoras": impressoras_data, "logs": logs}

# Endpoints de Impressão
def executar_impressao_comum(nome_impressora, texto, formatacao: Formatacao):
    try:
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nome_impressora)
        # Título do documento sem caracteres especiais para evitar conflitos no spooler antigo
        hdc.StartDoc("Printer_API_Job")
        hdc.StartPage()
        weight = 700 if formatacao.negrito else 400
        font = win32ui.CreateFont({"name": "Arial", "height": formatacao.tamanho, "weight": weight})
        hdc.SelectObject(font)
        y = 100
        for linha in texto.split("\n"):
            hdc.TextOut(100, y, linha)
            y += int(formatacao.tamanho * 1.5)
        hdc.EndPage(); hdc.EndDoc(); hdc.DeleteDC()
        logger.info(f"Sucesso: Impressao enviada para '{nome_impressora}'")
    except Exception as e: 
        logger.error(f"Falha na impressao comum: {e}")

def executar_impressao_zebra(nome_impressora, zpl_code):
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        win32print.StartDocPrinter(hPrinter, 1, ("Etiqueta_ZPL", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl_code.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter); win32print.EndDocPrinter(hPrinter); win32print.ClosePrinter(hPrinter)
        logger.info(f"Sucesso: ZPL enviado para '{nome_impressora}'")
    except Exception as e: 
        logger.error(f"Falha na impressao Zebra: {e}")

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    data = get_system_data()
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "impressoras": data["impressoras"],
        "logs": data["logs"],
        "api_key_exemplo": API_KEY
    })

@app.get("/api/status")
async def api_status():
    return get_system_data()

@app.get("/impressoras", dependencies=[Depends(verify_api_key)])
async def listar_impressoras():
    data = get_system_data()
    return {"impressoras": [imp["nome"] for imp in data["impressoras"]]}

@app.post("/imprimir", dependencies=[Depends(verify_api_key)])
async def imprimir(pedido: ImpressaoRequest, background_tasks: BackgroundTasks):
    nome_impressora = pedido.impressora if pedido.impressora else IMPRESSORA_PADRAO
    job_id = str(uuid.uuid4())[:8]
    if pedido.tipo == "zebra":
        background_tasks.add_task(executar_impressao_zebra, nome_impressora, pedido.conteudo)
    else:
        background_tasks.add_task(executar_impressao_comum, nome_impressora, pedido.conteudo, pedido.formatacao)
    return {"job_id": job_id, "status": "Enviado para fila", "impressora": nome_impressora}

if __name__ == "__main__":
    # Garante que o uvicorn também saiba que estamos em UTF-8
    uvicorn.run(app, host="0.0.0.0", port=PORTA_API)
