# 🗄️ Histórico de Layouts - Printer API

Este arquivo cataloga as versões do painel administrativo para facilitar a restauração rápida.

| Versão | Data | Nome | Características Principais | Arquivo |
| :--- | :--- | :--- | :--- | :--- |
| **v4.3** | 18/03/2026 | **Responsive Fluid Console** | Habilitado scroll vertical responsivo, remoção de overflow-hidden global, ajuste de min-height. | `backups/admin_v4.3_responsive_fluid.html` |
| **v4.2** | 18/03/2026 | **Enhanced Dark Console** | Legibilidade aumentada (alto contraste), efeito de lanterna global seguindo o mouse, refinamento de bordas. | `backups/admin_v4.2_enhanced_dark.html` |
| **v4.1** | 18/03/2026 | **Compact Dark Gateway** | Layout escuro profundo, cards compactos (5 p/ linha), logs visíveis em 60% da tela, branding profissional. | `backups/admin_v4.1_compact_dark.html` |
| **v4.0** | 18/03/2026 | **Aura Dark Full** | Layout Aura Dark inicial com cards grandes e efeito flashlight intenso. | `backups/admin_v4.0_aura_dark.html` |

---
**Como restaurar:**
Copie o conteúdo do arquivo desejado em `templates/backups/` e substitua o conteúdo de `templates/admin.html`.
