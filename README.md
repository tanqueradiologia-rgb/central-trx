# Central TRX

Página de acompanhamento da TRX Diagnóstico Digital: clínicas particulares, licitações e prazos, quadro nacional.

- **Fonte da verdade:** as planilhas "Pipeline TRX — Prospecção (fonte da verdade)" (Google Sheets) e "Pipeline_Licitacoes.xlsx" (Google Drive). Toda edição é feita nelas.
- **Atualização:** a automação `.github/workflows/atualizar.yml` roda a cada 15 minutos, das 07h às 21h de Brasília. Ela lê as planilhas com uma conta de serviço do Google só de leitura, gera `dados_central.js` e publica no GitHub Pages.
- **Telefone e e-mail não entram na página.** O contato fica na planilha.

## Arquivos
| Arquivo | Função |
|---|---|
| `site/index.html` | a página |
| `scripts/buscar_planilhas.py` | baixa as duas planilhas |
| `scripts/build_central.py` | transforma as planilhas no arquivo de dados da página |
| `.github/workflows/atualizar.yml` | agenda e publica |

## Segredo necessário
`GOOGLE_SA_JSON` (Settings → Secrets and variables → Actions): conteúdo do arquivo JSON da chave da conta de serviço. As duas planilhas precisam estar compartilhadas com o e-mail dessa conta, como leitor.
