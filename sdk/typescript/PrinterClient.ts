/**
 * Printer API Gateway - Simplified TypeScript SDK
 */

export interface PrintRequest {
  num_pedido: string;
  impressora: string;
  conteudo: string;
}

export interface PrintResponse {
  status: string;
  num_pedido: string;
  tipo_detectado: string;
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
   * Envia um trabalho de impressão (Auto-detecta PDF, ZPL ou Texto).
   */
  async imprimir(num_pedido: string, impressora: string, conteudo: string): Promise<PrintResponse> {
    const response = await fetch(`${this.baseUrl}/imprimir`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ num_pedido, impressora, conteudo }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erro na API de impressão');
    }

    return await response.json();
  }

  /**
   * Lista todas as impressoras e seus status.
   */
  async listarImpressoras(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/impressoras`, {
      method: 'GET',
      headers: this.headers,
    });
    if (!response.ok) throw new Error('Falha ao listar impressoras');
    return await response.json();
  }
}
