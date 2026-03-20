// const PrinterGateway = require('./PrinterClient'); // No Node.js (CommonJS)
// import PrinterGateway from './PrinterClient.js'; // No Browser/ES Modules

const client = new PrinterGateway('http://localhost:5000', 'minha_chave_segura_123');

async function testar() {
  try {
    // 1. Listar impressoras
    const printers = await client.listPrinters();
    console.log(`Impressoras: ${printers.length}`);

    // 2. Imprimir Texto
    console.log('Enviando texto via JS...');
    const res = await client.printText('Olá do SDK JavaScript!', { 
      bold: true, 
      size: 45 
    });
    console.log('Sucesso:', res);

  } catch (error) {
    console.error('Erro:', error.message);
  }
}

testar();
