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

## Segredos necessários (Settings → Secrets and variables → Actions)
- `GOOGLE_SA_JSON`: conteúdo do arquivo JSON da chave da conta de serviço. As planilhas precisam estar compartilhadas com o e-mail dessa conta, como leitor.
- `CENTRAL_SENHA`: senha da equipe (8 caracteres ou mais). Desde 20/10/2026 a página publica só `central.enc`: `dados_central.js`, `saude.js` e `roteiro.js` são cifrados (PBKDF2 + AES-256-GCM, `scripts/cifrar_central.py`) e apagados antes da publicação. A página pede a senha uma vez e a guarda no navegador; o botão Sair apaga. Para trocar a senha: trocar o segredo, rodar o workflow e avisar a equipe. Sem o segredo a rodada falha e nada é publicado.

## O que continua público
O repositório é público: `config/roteiro.json`, `apps-script/Codigo.gs` (com o roteiro embutido) e os IDs das planilhas ficam visíveis no GitHub, mesmo com a página cifrada. Para esconder também isso, o repositório precisa virar privado (GitHub Pages em repositório privado exige plano pago) ou o roteiro precisa sair do repositório.

## Central TRX · Edição (Apps Script)
A pasta `apps-script/` tem o app de edição das clínicas. Ele é um projeto Apps Script próprio (separado dos scripts que já existem na planilha) e abre a Pipeline TRX pelo ID:
- `Codigo.gs`: lê e grava na aba Pipeline; registra cada mudança e cada nota na aba Historico; avisa por e-mail quem foi marcado (lista na aba Equipe).
- `Index.html`: a tela.
- `appsscript.json`: fuso de Brasília e implantação como app da Web executado com o login de quem acessa.

Só grava as colunas liberadas em `FRENTES.clinicas.edicao`. Licitações e quadro entram como novas frentes depois que a Pipeline_Licitacoes virar Google Sheets.
