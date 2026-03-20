# 🖨️ Windows Printer API Gateway

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Windows Only](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)

Uma solução robusta e moderna para gerenciamento de impressões em ambiente Windows. Atua como um Gateway unificado para impressoras térmicas (Zebra/ZPL), documentos PDF e impressões de texto comuns (GDI), apresentando uma interface ultra-simplificada de apenas 3 parâmetros.

## ✨ Destaques

-   **🚀 Interface de 3 Parâmetros**: Envie apenas `num_pedido`, `impressora` e `conteudo`.
-   **🔍 Auto-Detecção Inteligente**: Detecta automaticamente se o conteúdo é **PDF (Base64)**, **ZPL (Zebra)** ou **Texto Comum**.
-   **📊 Dashboard Aura Design**: Monitoramento em tempo real via WebSockets com visual dark futurista.
-   **🛡️ Segurança Industrial**: Autenticação via `X-Api-Key` e sanitização automática de nomes de impressoras.
-   **🛰️ Hardware Monitoring**: Leitura de bitmask do spooler para detectar falta de papel, offline ou erros críticos.

---

## 🛠️ Tecnologias Core

-   **Backend**: FastAPI (Python 3.12)
-   **Spooler Access**: `pywin32` (win32print, win32ui)
-   **Real-time**: WebSockets para logs e status de hardware.
-   **Frontend**: HTML5/CSS3 (Aura Design System) integrado com Jinja2.

---

## 🚀 Como Começar

### Pré-requisitos
-   Windows 10/11 ou Windows Server 2019/2022.
-   [Python 3.12+](https://www.python.org/) ou [uv](https://github.com/astral-sh/uv).

### Instalação Rápida
1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/printer-api.git
    cd printer-api
    ```
2.  Configure o ambiente:
    ```bash
    cp .env.example .env  # Configure sua API_KEY aqui
    uv sync               # Ou: pip install -r requirements.txt
    ```
3.  Inicie o servidor:
    ```bash
    python main.py
    ```
4.  Acesse o Dashboard: `http://localhost:5000/admin`

---

## 🔌 API Reference

### Imprimir Documento
`POST /imprimir`

**Headers:**
- `X-Api-Key`: `sua_chave_aqui`
- `Content-Type`: `application/json`

**Payload:**
```json
{
  "num_pedido": "2025-001",
  "impressora": "Zebra ZD220",
  "conteudo": "^XA^FO50,50^A0N,50,50^FDPRODUTO TESTE^FS^XZ"
}
```

> **Nota**: O sistema aceita o nome da impressora com ou sem aspas e limpa espaços automaticamente.

---

## 📦 SDKs Disponíveis

Acelere sua integração utilizando nossos clientes nativos localizados na pasta `/sdk`:
-   **Python**: `sdk/python/printer_client.py`
-   **TypeScript**: `sdk/typescript/PrinterClient.ts`
-   **JavaScript**: `sdk/javascript/PrinterClient.js`

---

## 🐳 Docker (Windows Containers)

Este projeto suporta execução via Docker utilizando **Windows Server Core**. É obrigatório o uso de isolamento de processo para acessar o Spooler do host:

```bash
docker build -t printer-api .
docker run -d -p 5000:5000 --isolation=process --name printer-gateway printer-api
```

---

## 📖 Documentação Adicional

Para detalhes técnicos profundos sobre a configuração do Windows Spooler e deploy em produção, consulte o [SETUP_GUIDE.md](./SETUP_GUIDE.md).

---
*Desenvolvido para ambientes de logística e varejo que exigem alta disponibilidade e rastreabilidade.*
