# Passo a Passo: Criação da Printer API

Este guia detalha como criar uma API em Python para gerenciar impressões (Zebra/ZPL e impressoras comuns) utilizando **FastAPI** e **pywin32**.

## 1. Pré-requisitos
*   Python 3.12 ou superior instalado.
*   [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes rápido para Python).

## 2. Inicialização do Projeto
Abra o terminal na pasta desejada e execute:
```bash
uv init printer-api
cd printer-api
```

## 3. Instalação de Dependências
Adicione o FastAPI e a biblioteca para comunicação com a API do Windows:
```bash
uv add "fastapi[standard]" pywin32
```

## 4. Estrutura do Código (`main.py`)
Crie o arquivo `main.py` com as seguintes funcionalidades:

### Importações Necessárias
Utilizamos `win32print` para envio de dados brutos (RAW) e `win32ui` para desenhar documentos em impressoras comuns.

### Definição do Modelo de Dados
Usamos `Pydantic` para validar o corpo da requisição:
```python
class ImpressaoRequest(BaseModel):
    tipo: str        # 'zebra' ou 'comum'
    conteudo: str    # Código ZPL ou Texto simples
```

### Funções de Impressão
1.  **`imprimir_na_zebra`**: Abre a impressora em modo `RAW`. Essencial para que a impressora Zebra interprete os comandos ZPL (`^XA...^XZ`) em vez de imprimir o código como texto.
2.  **`imprimir_na_comum`**: Cria um "Contexto de Dispositivo" (DC), define uma fonte e desenha o texto linha por linha.

### Endpoint da API
Criamos uma rota `POST /imprimir` que decide qual função chamar baseada no campo `tipo`.

## 5. Execução da API
Para rodar o servidor:
```bash
python main.py
```
A API ficará disponível em `http://127.0.0.1:5000`.

## 6. Como Testar

### Teste de Impressão Comum (Geração de PDF)
```bash
curl -X POST http://127.0.0.1:5000/imprimir \
-H "Content-Type: application/json" \
-d "{\"tipo\": \"comum\", \"conteudo\": \"Pedido #123\nCliente: Allan\nTotal: R$ 50,00\"}"
```

### Teste de Etiqueta Zebra (ZPL)
```bash
curl -X POST http://127.0.0.1:5000/imprimir \
-H "Content-Type: application/json" \
-d "{\"tipo\": \"zebra\", \"conteudo\": \"^XA^FO50,50^A0N,50,50^FDTeste Zebra^FS^XZ\"}"
```

## Notas Importantes
*   **Nome da Impressora**: No código, a variável `IMPRESSORA_PDF` está definida como `"Microsoft Print to PDF"`. Em produção, altere para o nome exato da sua impressora instalada no Windows.
*   **Modo RAW**: A Zebra só funciona corretamente se o `StartDocPrinter` for chamado com o tipo `"RAW"`.
