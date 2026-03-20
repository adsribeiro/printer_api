import { PrinterGateway, PrinterInfo } from './PrinterClient';

const gateway = new PrinterGateway('http://localhost:5000', 'minha_chave_segura_123');

async function main() {
  try {
    console.log('--- Iniciando Teste SDK TypeScript ---');

    // 1. Listagem de Impressoras (Tipada)
    const { impressoras } = await gateway.listPrinters();
    console.log(`Printers disponíveis: ${impressoras.join(', ')}`);

    // 2. Impressão de Texto com Formatação
    console.log('Enviando job de texto...');
    const res = await gateway.printText('Teste via TypeScript SDK', {
      bold: true,
      size: 48,
      printerName: 'Microsoft Print to PDF'
    });
    console.log(`Sucesso! Job ID: ${res.job_id}`);

    // 3. Monitoramento Completo (Acesso aos metadados de hardware)
    const status = await gateway.getFullStatus();
    status.impressoras.forEach((info: PrinterInfo) => {
      console.log(`[${info.nome}] Status: ${info.status_principal} - Fila: ${info.trabalhos_na_fila}`);
    });

  } catch (error) {
    if (error instanceof Error) {
      console.error(`Erro na integração: ${error.message}`);
    }
  }
}

main();
