import os
import logging
import uuid
import sys
import time
import base64
import tempfile
import asyncio
import json
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
import win32print
import win32ui
import win32con
import win32api
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from dotenv import load_dotenv

# 1. Configuração e Logging (UTF-8 Hardened)
load_dotenv()

log_file = "printer_api.log"
logger = logging.getLogger("PrinterAPI")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)

logger.propagate = False

IMPRESSORA_PADRAO = os.getenv("IMPRESSORA_PADRAO", "Microsoft Print to PDF")
PORTA_API = int(os.getenv("PORTA_API", 5000))
API_KEY = os.getenv("API_KEY", "minha_chave_segura_123")

# 2. WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass 

manager = ConnectionManager()

# Mapeamento expandido de status do Windows Spooler
PRINTER_STATUS_FLAGS = {
    win32print.PRINTER_STATUS_PAUSED: "Pausada",
    win32print.PRINTER_STATUS_ERROR: "Erro Crítico",
    win32print.PRINTER_STATUS_PENDING_DELETION: "Exclusão Pendente",
    win32print.PRINTER_STATUS_PAPER_JAM: "Atolamento de Papel",
    win32print.PRINTER_STATUS_PAPER_OUT: "Sem Papel",
    win32print.PRINTER_STATUS_MANUAL_FEED: "Alimentação Manual",
    win32print.PRINTER_STATUS_PAPER_PROBLEM: "Problema no Papel",
    win32print.PRINTER_STATUS_OFFLINE: "Offline",
    win32print.PRINTER_STATUS_IO_ACTIVE: "I/O Ativo",
    win32print.PRINTER_STATUS_BUSY: "Ocupada",
    win32print.PRINTER_STATUS_PRINTING: "Imprimindo...",
    win32print.PRINTER_STATUS_OUTPUT_BIN_FULL: "Bandeja de Saída Cheia",
    win32print.PRINTER_STATUS_NOT_AVAILABLE: "Não Disponível",
    win32print.PRINTER_STATUS_WAITING: "Aguardando...",
    win32print.PRINTER_STATUS_PROCESSING: "Processando...",
    win32print.PRINTER_STATUS_INITIALIZING: "Inicializando...",
    win32print.PRINTER_STATUS_WARMING_UP: "Aquecendo...",
    win32print.PRINTER_STATUS_TONER_LOW: "Toner Baixo",
    win32print.PRINTER_STATUS_NO_TONER: "Sem Toner",
    win32print.PRINTER_STATUS_PAGE_PUNT: "Erro de Página",
    win32print.PRINTER_STATUS_USER_INTERVENTION: "Intervenção do Usuário",
    win32print.PRINTER_STATUS_OUT_OF_MEMORY: "Sem Memória",
    win32print.PRINTER_STATUS_DOOR_OPEN: "Tampa Aberta",
    win32print.PRINTER_STATUS_SERVER_UNKNOWN: "Servidor Desconhecido",
    win32print.PRINTER_STATUS_POWER_SAVE: "Economia de Energia",
}

def parse_printer_status(status_code: int) -> List[str]:
    """Analisa o bitmask de status da impressora."""
    if status_code == 0:
        return ["Pronta"]
    
    found_statuses = []
    for flag, label in PRINTER_STATUS_FLAGS.items():
        if status_code & flag:
            found_statuses.append(label)
            
    return found_statuses if found_statuses else [f"Status {status_code}"]

def get_system_data():
    impressoras_data = []
    try:
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for imp in impressoras:
            try:
                hPrinter = win32print.OpenPrinter(imp[2])
                info = win32print.GetPrinter(hPrinter, 2)
                
                # Coleta metadados avançados
                status_list = parse_printer_status(info['Status'])
                
                impressoras_data.append({
                    "nome": str(imp[2]),
                    "status_list": status_list,
                    "status_principal": status_list[0],
                    "trabalhos_na_fila": info['cJobs'],
                    "driver": str(info['pDriverName']),
                    "porta": str(info['pPortName']),
                    "local": str(info['pLocation']) or "Local",
                    "comentario": str(info['pComment'])
                })
                win32print.ClosePrinter(hPrinter)
            except Exception as e_inner:
                logger.error(f"Erro ao abrir impressora {imp[2]}: {e_inner}")
    except Exception as e:
        logger.error(f"Erro ao listar impressoras: {e}")

    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding='utf-8', errors='replace') as f:
                logs = [line.strip() for line in f.readlines()[-25:]]
        except Exception as e:
            logger.error(f"Erro ao ler log: {e}")
    
    return {"impressoras": impressoras_data, "logs": logs}

async def broadcast_updates():
    while True:
        try:
            if manager.active_connections:
                data = get_system_data()
                await manager.broadcast(json.dumps(data))
        except Exception as e:
            logger.error(f"Erro no loop de broadcast: {e}")
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_updates())
    yield
    task.cancel()

app = FastAPI(title="Printer API - Gateway Edition", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Acesso negado: Chave de API inválida.")
    return x_api_key

class Formatacao(BaseModel):
    negrito: bool = False
    tamanho: int = 40
    alinhamento: str = "left"

class ImpressaoRequest(BaseModel):
    tipo: str # "comum", "zebra", "pdf"
    conteudo: str 
    impressora: Optional[str] = None
    formatacao: Optional[Formatacao] = Formatacao()
    forcar: bool = False # Se True, ignora avisos de hardware

# Motores de Impressão
async def executar_impressao_comum(nome_impressora, texto, formatacao: Formatacao):
    try:
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nome_impressora)
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
        logger.info(f"Sucesso: Impressao comum enviada para '{nome_impressora}'")
        await manager.broadcast(json.dumps(get_system_data()))
    except Exception as e: 
        logger.error(f"Falha na impressao comum: {e}")

async def executar_impressao_zebra(nome_impressora, zpl_code):
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        win32print.StartDocPrinter(hPrinter, 1, ("Etiqueta_ZPL", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl_code.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter); win32print.EndDocPrinter(hPrinter); win32print.ClosePrinter(hPrinter)
        logger.info(f"Sucesso: ZPL enviado para '{nome_impressora}'")
        await manager.broadcast(json.dumps(get_system_data()))
    except Exception as e: 
        logger.error(f"Falha na impressao Zebra: {e}")

async def executar_impressao_pdf(nome_impressora, caminho_pdf):
    try:
        win32api.ShellExecute(0, "printto", caminho_pdf, f'"{nome_impressora}"', ".", 0)
        logger.info(f"Sucesso: PDF enviado para o spooler da '{nome_impressora}'")
        await manager.broadcast(json.dumps(get_system_data()))
        await asyncio.sleep(10)
        if os.path.exists(caminho_pdf):
            os.remove(caminho_pdf)
            logger.info(f"Arquivo temporario removido: {caminho_pdf}")
    except Exception as e:
        logger.error(f"Falha na impressao PDF: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps(get_system_data()))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request": request, 
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
    
    # 1. Validação de Hardware Pré-Impressão
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        info = win32print.GetPrinter(hPrinter, 2)
        win32print.ClosePrinter(hPrinter)
        
        status_code = info['Status']
        # Status Críticos que impedem impressão
        status_criticos = (win32print.PRINTER_STATUS_OFFLINE | 
                           win32print.PRINTER_STATUS_ERROR | 
                           win32print.PRINTER_STATUS_PAPER_OUT |
                           win32print.PRINTER_STATUS_PAPER_JAM |
                           win32print.PRINTER_STATUS_DOOR_OPEN)
        
        if (status_code & status_criticos) and not pedido.forcar:
            status_labels = ", ".join(parse_printer_status(status_code))
            logger.warning(f"Impressão rejeitada para '{nome_impressora}': {status_labels}")
            raise HTTPException(
                status_code=503, 
                detail=f"Impressora não está pronta para receber trabalhos. Status: {status_labels}. Use 'forcar': true para ignorar."
            )
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        logger.error(f"Erro ao validar impressora '{nome_impressora}': {e}")
        # Se não conseguir abrir a impressora, ela provavelmente não existe ou está inacessível
        raise HTTPException(status_code=404, detail=f"Impressora '{nome_impressora}' não encontrada ou inacessível.")

    job_id = str(uuid.uuid4())[:8]
    
    if pedido.tipo == "zebra":
        background_tasks.add_task(executar_impressao_zebra, nome_impressora, pedido.conteudo)
    elif pedido.tipo == "pdf":
        try:
            pdf_bytes = base64.b64decode(pedido.conteudo)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                caminho_temp = tmp.name
            background_tasks.add_task(executar_impressao_pdf, nome_impressora, caminho_temp)
            logger.info(f"Processando PDF em Background. Temp: {caminho_temp}")
        except Exception as e:
            logger.error(f"Erro ao processar Base64 de PDF: {e}")
            raise HTTPException(status_code=400, detail="Conteudo do PDF invalido (Base64 esperado).")
    else:
        background_tasks.add_task(executar_impressao_comum, nome_impressora, pedido.conteudo, pedido.formatacao)
    
    await manager.broadcast(json.dumps(get_system_data()))
    
    return {"job_id": job_id, "status": "Processando em segundo plano", "impressora": nome_impressora}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORTA_API)
