import win32print
import win32ui
import win32con
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class ImpressaoRequest(BaseModel):
    tipo: str
    conteudo: str


IMPRESSORA_PDF = "Microsoft Print to PDF"


def imprimir_na_comum(nome_impressora, texto):
    try:
        # Cria um contexto de dispositivo para a impressora
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(nome_impressora)

        # Inicia o documento
        hdc.StartDoc("Pedido Web")
        hdc.StartPage()

        # Configura uma fonte simples
        font = win32ui.CreateFont(
            {
                "name": "Arial",
                "height": 40,
                "weight": 400,
            }
        )
        hdc.SelectObject(font)

        # "Desenha" o texto no PDF (X, Y, Texto)
        # Dividindo por linhas para o PDF não sair em uma linha só
        y = 100
        for linha in texto.split("\n"):
            hdc.TextOut(100, y, linha)
            y += 60  # Pula linha

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
    except Exception as e:
        raise Exception(f"Erro ao gerar PDF: {e}")


def imprimir_na_zebra(nome_impressora, zpl_code):
    # Zebra PRECISA do modo RAW para interpretar o código ^XA ^XZ
    hPrinter = win32print.OpenPrinter(nome_impressora)
    try:
        job = win32print.StartDocPrinter(hPrinter, 1, ("Etiqueta Zebra", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, zpl_code.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)


@app.post("/imprimir")
async def imprimir(pedido: ImpressaoRequest):
    try:
        if pedido.tipo == "zebra":
            # Se for Zebra, enviamos RAW (mesmo que o PDF saia "inválido", na Zebra real funcionará)
            imprimir_na_zebra(IMPRESSORA_PDF, pedido.conteudo)
            return {"status": "Enviado ZPL (RAW)"}
        else:
            # Se for Comum, usamos a lógica de desenho de texto para o PDF sair bonito
            imprimir_na_comum(IMPRESSORA_PDF, pedido.conteudo)
            return {"status": "PDF gerado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Rodando com uvicorn através do próprio script
    uvicorn.run(app, host="127.0.0.1", port=5000)
