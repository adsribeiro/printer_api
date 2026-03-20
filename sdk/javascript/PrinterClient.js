/**
 * @class PrinterGateway
 * @description SDK JavaScript/Node.js para integração com o Printer API Gateway.
 */
class PrinterGateway {
  /**
   * @param {string} baseUrl - URL base da API (ex: http://localhost:5000)
   * @param {string} apiKey - Chave de API configurada no .env
   */
  constructor(baseUrl = 'http://localhost:5000', apiKey = 'minha_chave_segura_123') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.headers = {
      'X-Api-Key': this.apiKey,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Retorna a lista de impressoras disponíveis.
   */
  async listPrinters() {
    const response = await fetch(`${this.baseUrl}/impressoras`, {
      method: 'GET',
      headers: this.headers
    });
    if (!response.ok) throw new Error(`Erro: ${response.statusText}`);
    return await response.json();
  }

  /**
   * Imprime texto formatado (GDI).
   */
  async printText(content, { printerName = null, bold = false, size = 40, force = false } = {}) {
    const payload = {
      tipo: 'comum',
      conteudo: content,
      impressora: printerName,
      formatacao: { negrito: bold, tamanho: size },
      forcar: force
    };
    return await this._sendPrintJob(payload);
  }

  /**
   * Imprime comandos RAW Zebra (ZPL).
   */
  async printZpl(zplString, { printerName = null, force = false } = {}) {
    const payload = {
      tipo: 'zebra',
      conteudo: zplString,
      impressora: printerName,
      forcar: force
    };
    return await this._sendPrintJob(payload);
  }

  /**
   * Imprime um documento PDF (Base64).
   */
  async printPdf(base64Content, { printerName = null, force = false } = {}) {
    const payload = {
      tipo: 'pdf',
      conteudo: base64Content,
      impressora: printerName,
      forcar: force
    };
    return await this._sendPrintJob(payload);
  }

  /**
   * @private
   */
  async _sendPrintJob(payload) {
    const response = await fetch(`${this.baseUrl}/imprimir`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`Erro: ${response.statusText}`);
    return await response.json();
  }
}

// Exportação para Node.js (CommonJS ou ES Modules se necessário)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = PrinterGateway;
}
