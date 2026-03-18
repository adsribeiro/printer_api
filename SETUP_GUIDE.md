# Setup & Architecture Guide: Printer API Gateway

Este guia técnico detalha a infraestrutura, configuração e operação da **Printer API Gateway**, uma solução robusta em Python para gerenciamento de impressões (ZPL, PDF e GDI) em ambientes Windows.

---

## 🛠️ 1. Stack Tecnológica
*   **Engine**: Python 3.12+ (Otimizado via [uv](https://docs.astral.sh/uv/)).
*   **Framework**: FastAPI (Async/Await) para alta performance.
*   **Comunicação Real-time**: WebSockets para streaming de logs e status.
*   **Interface**: Jinja2 + Tailwind CSS (Aura Design System v5.0).
*   **Integração Windows**: `pywin32` (win32print, win32ui, win32api).

---

## ⚙️ 2. Instalação e Preparação

### Inicialização
```bash
uv init printer-api
cd printer-api
```

### Dependências Críticas
```bash
uv add "fastapi[standard]" pywin32 python-dotenv requests
```

---

## 🛰️ 3. Arquitetura do Sistema (`main.py`)

O Gateway opera em três camadas principais:

### A. Camada de Segurança
Implementa autenticação via Header `X-Api-Key`, validada em todos os endpoints de escrita.

### B. Camada de Processamento (Print Engines)
1.  **GDI Engine (`comum`)**: Renderiza texto diretamente no Canvas do Windows, suportando formatação (negrito/tamanho).
2.  **ZPL RAW Engine (`zebra`)**: Envia comandos de baixo nível para impressoras térmicas Zebra.
3.  **PDF Engine (`pdf`)**: Decodifica Base64, gera buffer temporário e utiliza `ShellExecute` para impressão silenciosa.

### C. Camada Real-time (WebSockets)
Utiliza um `ConnectionManager` para gerenciar conexões persistentes com o Dashboard Administrativo, realizando broadcast de eventos instantaneamente.

---

## 🖥️ 4. Console Administrativo
O painel pode ser acessado em `http://localhost:5000/admin`.
*   **Monitor de Hardware**: Status em tempo real das impressoras locais e de rede.
*   **Live Stream**: Terminal de logs via WebSocket (v5.0).
*   **Efeito Visual**: Interface Dark Mode com "Mouse Glow Effect".

---

## 🔌 5. Guia de Integração (API Reference)

### Endpoint Principal: `POST /imprimir`
**Headers:**
```json
{
  "X-Api-Key": "sua_chave_definida_no_env",
  "Content-Type": "application/json"
}
```

### Exemplos de Payload:

**1. Impressão Comum (Texto):**
```json
{
  "tipo": "comum",
  "conteudo": "Linha 1\nLinha 2",
  "formatacao": { "negrito": true, "tamanho": 40 }
}
```

**2. Etiqueta Zebra (ZPL):**
```json
{
  "tipo": "zebra",
  "conteudo": "^XA^FO50,50^A0N,50,50^FDPRODUTO TESTE^FS^XZ"
}
```

**3. Documento PDF (Base64):**
```json
{
  "tipo": "pdf",
  "conteudo": "JVBERi0xLjQKJ..." // String Base64 do arquivo
}
```

---

## 📝 6. Notas de Operação
*   **Encoding**: Todo o sistema é **UTF-8 Hardened**. Logs e mensagens suportam acentuação brasileira completa.
*   **Fila Assíncrona**: A API utiliza `BackgroundTasks`. O retorno `200 OK` significa que o trabalho foi aceito e está sendo processado pelo spooler do Windows.
*   **Manutenção de Layout**: Versões anteriores do dashboard são preservadas em `templates/backups/`.
