# Roadmap de Evolução: Printer API v1

Este documento estabelece as fases de melhoria para transformar o protótipo atual em uma solução de impressão robusta e pronta para produção.

---

## 🚀 Fase 1: Estabilização e Configuração (Concluída ✅)
- [x] **Configuração Dinâmica**: Mover o nome da impressora (`IMPRESSORA_PDF`) para variáveis de ambiente (`.env`) ou um arquivo `config.yaml`.
- [x] **Tratamento de Erros Refinado**: Criar exceções personalizadas para casos como "Impressora Offline", "Papel Acabou" ou "Driver não Encontrado".
- [x] **Logging Profissional**: Implementar a biblioteca `logging` para registrar cada tentativa de impressão, sucessos e falhas em arquivos de log rotativos.
- [x] **Listagem de Impressoras**: Criar um endpoint `GET /impressoras` que retorne a lista de impressoras instaladas no Windows para facilitar a configuração.

## 🛠️ Fase 2: Funcionalidades Avançadas (Concluída ✅)
- [x] **Suporte a Múltiplas Impressoras**: Permitir que o JSON da requisição especifique qual impressora usar (ex: `{"impressora": "Zebra_Cozinha", ...}`).
- [x] **Suporte a PDFs Reais**: Implementar a impressão direta de arquivos PDF existentes utilizando `ShellExecute` do Windows.
- [x] **Formatação de Texto (Comum)**: Adicionar suporte a negrito, tamanhos de fonte variáveis e alinhamento no modo de impressão comum.
- [x] **Fila de Impressão Interna**: Usar `BackgroundTasks` do FastAPI para que a API responda imediatamente enquanto a impressão ocorre de forma assíncrona.

## 📊 Fase 3: Monitoramento e Interface (Concluída ✅)
- [x] **Painel Administrativo (UI)**: Uma pequena interface web integrada (FastAPI + Jinja2) para visualizar o status das impressoras e logs recentes.
- [x] **Monitor de Status da Fila**: Integrar com a API do Windows para retornar o status real do trabalho de impressão (ex: `Printing`, `Paused`, `Error`).
- [x] **Autenticação**: Implementar `API Key` simples para evitar que qualquer pessoa na rede dispare impressões indesejadas.

## 🌐 Fase 4: Escalabilidade e Ecossistema (Futuro 🚀)
- [ ] **WebSockets**: Notificações em tempo real para o cliente quando uma impressão for concluída ou falhar.
- [ ] **Dockerização (Windows Containers)**: Preparar a API para rodar em containers Windows, facilitando o deploy.
- [ ] **SDK Client**: Criar uma biblioteca pequena em Python/JS para que outros sistemas da empresa consumam a API de forma padronizada.

---

## 📈 Métricas de Sucesso
1. **Latência**: Resposta do endpoint abaixo de 100ms.
2. **Confiabilidade**: 99.9% de sucesso no envio para o spooler do Windows.
3. **Facilidade**: Tempo de setup em novas máquinas inferior a 5 minutos.
