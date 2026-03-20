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
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
import uvicorn
from dotenv import load_dotenv

# 1. Configuração e Logging
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

API_KEY = os.getenv("API_KEY", "minha_chave_segura_123")
PORTA_API = int(os.getenv("PORTA_API", 5000))

# 2. WebSocket Manager
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
            except Exception: pass 

manager = ConnectionManager()

# 3. Modelos com Sanitização Profissional
class ImpressaoRequest(BaseModel):
    num_pedido: str
    impressora: str
    conteudo: str

    @field_validator('impressora', 'num_pedido', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            # Remove aspas duplas, simples e espaços em branco nas extremidades
            return v.strip().strip('"').strip("'").strip()
        return v

def detectar_tipo_impressao(conteudo: str) -> str:
    if conteudo.startswith("JVBERi"): return "pdf"
    if conteudo.strip().startswith("^XA"): return "zebra"
    return "comum"

def parse_printer_status(status_code: int) -> List[str]:
    PRINTER_STATUS_FLAGS = {
        win32print.PRINTER_STATUS_PAUSED: "Pausada",
        win32print.PRINTER_STATUS_ERROR: "Erro Critico",
        win32print.PRINTER_STATUS_PAPER_OUT: "Sem Papel",
        win32print.PRINTER_STATUS_OFFLINE: "Offline",
        win32print.PRINTER_STATUS_BUSY: "Ocupada",
    }
    if status_code == 0: return ["Pronta"]
    found = [label for flag, label in PRINTER_STATUS_FLAGS.items() if status_code & flag]
    return found if found else [f"Status {status_code}"]

def get_system_data():
    impressoras_data = []
    try:
        impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for imp in impressoras:
            try:
                hPrinter = win32print.OpenPrinter(imp[2])
                info = win32print.GetPrinter(hPrinter, 2)
                status_list = parse_printer_status(info['Status'])
                impressoras_data.append({
                    "nome": str(imp[2]),
                    "status_list": status_list,
                    "status_principal": status_list[0],
                    "trabalhos_na_fila": info['cJobs'],
                    "driver": str(info['pDriverName'])
                })
                win32print.ClosePrinter(hPrinter)
            except: pass
    except Exception as e: logger.error(f"Erro ao listar: {e}")

    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding='utf-8', errors='replace') as f:
            logs = [line.strip() for line in f.readlines()[-25:]]
    
    return {"impressoras": impressoras_data, "logs": logs}

async def broadcast_updates():
    while True:
        if manager.active_connections:
            await manager.broadcast(json.dumps(get_system_data()))
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_updates())
    yield
    task.cancel()

app = FastAPI(title="Printer API Gateway", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

# 4. Motores de Impressao
async def executar_impressao_comum(nome_impressora, texto, num_pedido):
    try:
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nome_impressora)
        hdc.StartDoc(f"Pedido_{num_pedido}")
        hdc.StartPage()
        font = win32ui.CreateFont({"name": "Arial", "height": 40, "weight": 400})
        hdc.SelectObject(font)
        y = 100
        for linha in texto.split("\n"):
            hdc.TextOut(100, y, linha)
            y += 60
        hdc.EndPage(); hdc.EndDoc(); hdc.DeleteDC()
        logger.info(f"Pedido {num_pedido}: Impressao concluida.")
        await manager.broadcast(json.dumps(get_system_data()))
    except Exception as e: logger.error(f"Pedido {num_pedido}: Erro GDI: {e}")

async def executar_impressao_zebra(nome_impressora, zpl_code, num_pedido):
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        win32print.StartDocPrinter(hPrinter, 1, (f"Pedido_{num_pedido}", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl_code.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter); win32print.EndDocPrinter(hPrinter); win32print.ClosePrinter(hPrinter)
        logger.info(f"Pedido {num_pedido}: ZPL enviado.")
        await manager.broadcast(json.dumps(get_system_data()))
    except Exception as e: logger.error(f"Pedido {num_pedido}: Erro ZPL: {e}")

async def executar_impressao_pdf(nome_impressora, caminho_pdf, num_pedido):
    try:
        win32api.ShellExecute(0, "printto", caminho_pdf, f'"{nome_impressora}"', ".", 0)
        logger.info(f"Pedido {num_pedido}: PDF enviado.")
        await manager.broadcast(json.dumps(get_system_data()))
        await asyncio.sleep(10)
        if os.path.exists(caminho_pdf): os.remove(caminho_pdf)
    except Exception as e: logger.error(f"Pedido {num_pedido}: Erro PDF: {e}")

# 5. Endpoints
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps(get_system_data()))
        while True: await websocket.receive_text()
    except WebSocketDisconnect: manager.disconnect(websocket)
    except Exception: manager.disconnect(websocket)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request, "api_key_exemplo": API_KEY})

@app.get("/api/status")
async def api_status(): return get_system_data()

@app.get("/impressoras")
async def listar_impressoras(x_api_key: str = Header(None)):
    if x_api_key != API_KEY: raise HTTPException(status_code=403, detail="Chave invalida")
    return get_system_data()

@app.post("/imprimir")
async def imprimir(pedido: ImpressaoRequest, x_api_key: str = Header(None), background_tasks: BackgroundTasks = BackgroundTasks()):
    if x_api_key != API_KEY: raise HTTPException(status_code=403, detail="Chave invalida")
    
    # Após a sanitização do Pydantic, a impressora virá sem aspas
    try:
        hPrinter = win32print.OpenPrinter(pedido.impressora)
        win32print.ClosePrinter(hPrinter)
    except:
        logger.error(f"Impressora '{pedido.impressora}' nao encontrada.")
        raise HTTPException(status_code=404, detail=f"Impressora '{pedido.impressora}' nao encontrada.")

    tipo = detectar_tipo_impressao(pedido.conteudo)
    if tipo == "zebra":
        background_tasks.add_task(executar_impressao_zebra, pedido.impressora, pedido.conteudo, pedido.num_pedido)
    elif tipo == "pdf":
        try:
            pdf_bytes = base64.b64decode(pedido.conteudo)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                caminho_temp = tmp.name
            background_tasks.add_task(executar_impressao_pdf, pedido.impressora, caminho_temp, pedido.num_pedido)
        except: raise HTTPException(status_code=400, detail="PDF Base64 invalido")
    else:
        background_tasks.add_task(executar_impressao_comum, pedido.impressora, pedido.conteudo, pedido.num_pedido)
    
    return {"status": "Aceito", "num_pedido": pedido.num_pedido, "tipo_detectado": tipo}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORTA_API)
