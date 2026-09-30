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

## Central TRX · Edição (Apps Script)
A pasta `apps-script/` tem o app de edição das clínicas. Ele é um projeto Apps Script próprio (separado dos scripts que já existem na planilha) e abre a Pipeline TRX pelo ID:
- `Codigo.gs`: lê e grava na aba Pipeline; registra cada mudança e cada nota na aba Historico; avisa por e-mail quem foi marcado (lista na aba Equipe).
- `Index.html`: a tela.
- `appsscript.json`: fuso de Brasília e implantação como app da Web executado com o login de quem acessa.

Só grava as colunas liberadas em `FRENTES.clinicas.edicao`. Licitações e quadro entram como novas frentes depois que a Pipeline_Licitacoes virar Google Sheets.
