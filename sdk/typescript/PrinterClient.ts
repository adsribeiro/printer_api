/**
 * Printer API Gateway - TypeScript SDK
 * Versão 1.0.0
 */

export type PrintType = 'comum' | 'zebra' | 'pdf';

export interface PrintFormat {
  negrito?: boolean;
  tamanho?: number;
  alinhamento?: 'left' | 'center';
}

export interface PrintRequest {
  tipo: PrintType;
  conteudo: string;
  impressora?: string | null;
  formatacao?: PrintFormat;
  forcar?: boolean;
}

export interface PrintResponse {
  job_id: string;
  status: string;
  impressora: string;
}

export interface PrinterInfo {
  nome: string;
  status_list: string[];
  status_principal: string;
  trabalhos_na_fila: number;
  driver: string;
  porta: string;
  local: string;
  comentario: string;
}

export class PrinterGateway {
  private baseUrl: string;
  private apiKey: string;

  constructor(baseUrl: string = 'http://localhost:5000', apiKey: string = 'minha_chave_segura_123') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
  }

  private get headers(): HeadersInit {
    return {
      'X-Api-Key': this.apiKey,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Obtém a lista completa de impressoras com metadados avançados.
   */
  async listPrinters(): Promise<{ impressoras: string[] }> {
    const response = await fetch(`${this.baseUrl}/impressoras`, {
      method: 'GET',
      headers: this.headers,
    });
    if (!response.ok) throw new Error(`Falha ao listar impressoras: ${response.statusText}`);
    return await response.json();
  }

  /**
   * Obtém o status detalhado do sistema (impressoras + logs).
   */
  async getFullStatus(): Promise<{ impressoras: PrinterInfo[]; logs: string[] }> {
    const response = await fetch(`${this.baseUrl}/api/status`, {
      method: 'GET',
      headers: this.headers,
    });
    if (!response.ok) throw new Error(`Falha ao obter status: ${response.statusText}`);
    return await response.json();
  }

  /**
   * Envia um trabalho de impressão de texto (GDI).
   */
  async printText(
    content: string, 
    options: { printerName?: string; bold?: boolean; size?: number; force?: boolean } = {}
  ): Promise<PrintResponse> {
    return this.sendPrintJob({
      tipo: 'comum',
      conteudo: content,
      impressora: options.printerName,
      formatacao: {
        negrito: options.bold,
        tamanho: options.size,
      },
      forcar: options.force,
    });
  }

  /**
   * Envia um trabalho de impressão ZPL (Zebra).
   */
  async printZpl(zpl: string, printerName?: string, force: boolean = false): Promise<PrintResponse> {
    return this.sendPrintJob({
      tipo: 'zebra',
      conteudo: zpl,
      impressora: printerName,
      forcar: force,
    });
  }

  /**
   * Envia um documento PDF (Base64).
   */
  async printPdf(base64: string, printerName?: string, force: boolean = false): Promise<PrintResponse> {
    return this.sendPrintJob({
      tipo: 'pdf',
      conteudo: base64,
      impressora: printerName,
      forcar: force,
    });
  }

  private async sendPrintJob(payload: PrintRequest): Promise<PrintResponse> {
    const response = await fetch(`${this.baseUrl}/imprimir`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro desconhecido na API de impressão');
    }

    return await response.json();
  }
}
