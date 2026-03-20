# Setup & Architecture Guide: Printer API Gateway

Este guia técnico detalha a infraestrutura e operação da **Printer API Gateway**. A API foi simplificada para facilitar a integração, exigindo apenas 3 parâmetros fundamentais.

---

## 🚀 1. Integração Simplificada

A API agora utiliza **Auto-detecção de Conteúdo**, eliminando a necessidade de especificar o tipo de impressão ou formatação complexa no payload inicial.

### Endpoint: `POST /imprimir`
**Payload Necessário:**
```json
{
  "num_pedido": "12345",
  "impressora": "Nome da Impressora no Windows",
  "conteudo": "Conteúdo para imprimir"
}
```

### 💡 Como a Detecção Funciona:
1.  **PDF**: Se o `conteudo` começar com `JVBERi` (Base64 de um PDF), a API processa como documento.
2.  **Zebra (ZPL)**: Se o `conteudo` começar com `^XA`, a API processa como etiqueta térmica.
3.  **Texto**: Qualquer outro conteúdo será impresso como texto simples (GDI) usando fonte padrão Arial 40.

---

## 📦 2. Usando os SDKs (Recomendado)

Os SDKs foram atualizados para suportar a nova interface simplificada.

### Python
```python
from printer_client import PrinterGateway

client = PrinterGateway(api_key="sua_chave")
# O SDK converte arquivos .pdf automaticamente para Base64 se você passar o caminho
client.imprimir(num_pedido="100", impressora="Zebra", conteudo="^XA...^XZ")
```

### TypeScript / JavaScript
```typescript
import { PrinterGateway } from './PrinterClient';

const client = new PrinterGateway('http://localhost:5000', 'sua_chave');
await client.imprimir("101", "Impressora PDF", "Texto simples ou Base64");
```

---

## 📝 3. Notas de Operação
*   **Segurança**: Header `X-Api-Key` é obrigatório.
*   **Rastreabilidade**: O `num_pedido` é utilizado como nome do trabalho no spooler do Windows, facilitando a identificação na fila física.
*   **WebSockets**: O Dashboard (`/admin`) continua recebendo atualizações em tempo real via WebSockets.
