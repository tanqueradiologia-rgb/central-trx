# Central TRX

Página de acompanhamento da TRX Diagnóstico Digital: clínicas particulares, licitações e prazos, quadro nacional.

- **Fonte da verdade:** as planilhas "Pipeline TRX — Prospecção (fonte da verdade)" (Google Sheets) e "Pipeline_Licitacoes.xlsx" (Google Drive). Toda edição é feita nelas.
- **Atualização:** a automação `.github/workflows/atualizar.yml` é agendada nos horários fixos 06h13, 08h13, 10h13, 12h13, 14h13, 16h13 e 18h13 de Brasília, mais uma rodada de hora em hora (minuto 37) que também roda o radar PNCP. O agendador do GitHub descarta parte dos gatilhos em repositório público, então nem todo horário dispara; o aviso amarelo da página só acende depois de 90 minutos sem rodada (m120, 05/11/2026). Quem garante a rodação é a tarefa agendada do Claude "TRX: disparar a Central no GitHub", que chama workflow_dispatch a cada hora no minuto 8, das 06h às 20h de Brasília; o cron do próprio workflow é a segunda via. Ela lê as planilhas com uma conta de serviço do Google só de leitura, gera `dados_central.js` e publica no GitHub Pages.
- **Telefone e e-mail não entram na página.** O contato fica na planilha.

## Arquivos
| Arquivo | Função |
|---|---|
| `site/index.html` | a página |
| `site/vendor/xlsx.mini.min.js` | SheetJS, lê a planilha de apuração no navegador |
| `scripts/buscar_planilhas.py` | baixa as duas planilhas |
| `scripts/build_central.py` | transforma as planilhas no arquivo de dados da página |
| `.github/workflows/atualizar.yml` | agenda e publica |

## Layout v2 (17/11/2026)
A página segue a linguagem do site trx.med.br: degradê navy→turquesa (#0e3958→#0094bd) na aba ativa, nos botões e no painel de abertura; fundo #f9fafb, bordas #d7dfea e cantos de 12px.
- A aba **Início** é a aba padrão e concentra o que antes aparecia em todas as abas: o painel do dia (números), a fila Hoje, as validades, os avisos do sistema, o resumo do ISGH e o Mural. As outras abas mostram só a própria frente.
- Na fila Hoje cada item ocupa uma linha; tocar abre o texto, os links e o Feito/Ciente/Observação.
- O resumo do ISGH mostra os três itens mais urgentes de cada bloco; o resto fica no dossiê (aba ISGH).
- Validades mostram cinco à vista; avisos do sistema e calendário do mês ficam recolhidos.

## Produção dos sócios (aba nova, 11/11/2026)
A aba **Produção dos sócios** da página mostra o coeficiente de esforço e o score de cada médico por período. Ela nasceu do pedido do Marcos de desenvolver com o Henrique (controle financeiro) a medição da produção dos sócios.

Três abas da Pipeline Licitações alimentam a aba, e a régua mora na planilha, não no código:
| Aba | O que guarda |
|---|---|
| `Producao_Params` | a régua: coeficiente de esforço por modalidade, peso dos quatro eixos, meta de margem, fator líquido da cascata e os SLA |
| `Producao_Socios` | um lançamento por período, médico, contrato e modalidade: exames, laudos no prazo, horas medianas, receita e repasse |
| `Escala_Socios` | plantões, sobreavisos e escalas devolvidas por médico no período |

O score é a média ponderada de quatro eixos (esforço, prazo, margem e cobertura de escala). **Eixo sem dado no período sai da conta e o peso dele é redistribuído entre os eixos medidos**, então a aba já serve antes de a escala estar preenchida. Mudar um coeficiente ou um peso na `Producao_Params` muda a página na rodada seguinte; mudança de régua passa pelo Marcos.

## Menu de sete abas (27/11/2026)
Roteiro (primeira, em destaque), Início, Listas, Resultados, Produção, Relatórios e Kit. A aba Listas reúne Clínicas, Licitações, Quadro público e Prioridades, com um seletor no alto. O ISGH não tem aba: entra na esteira como qualquer cliente, com a marca ISGH no texto, e o dossiê abre pelo endereço `#isgh`. O jurídico virou o índice de documentos, dentro do Roteiro e no endereço `#fiscal`.

## Fluxo: o Kanban da Central (27/11/2026)
A Central mede o fluxo das frentes e mostra o trabalho em quadro. Faturamento, Relatórios, Produção e Kit ficam fora, por decisão do Marcos.

| Onde | O que mostra |
|---|---|
| Início, Minha fila | quadro com A fazer, Fazendo, Com o Claude e Para revisar; trava com motivo; no máximo 3 em Fazendo por pessoa (avisa, não trava) |
| Clínicas e Licitações | botão Tabela ou Quadro; coluna "Na etapa" com os dias na etapa; faixa-resumo com em andamento, teto, fila, parados e carga por pessoa |
| Roteiro (primeira aba, em destaque) | o quadro das particulares com as seis etapas e a sétima coluna, Coordenação por cliente, que fecha o processo com os clientes em produção; os Objetivos da semana aparecem no cartão do cliente que citam; debaixo das sete colunas, duas faixas alinhadas às mesmas colunas: Setor público (licitações e quadro) e Jurídico e documentos (documentos de habilitação, prazos de edital e contratos); a aba Fiscal inteira abre recolhida no fim da página; quadros de Licitações e Quadro público ao lado |
| Resultados | bloco de fluxo: em andamento contra o teto, dias na etapa de cada item, passagens por semana, tempo por etapa e previsão por simulação |
| Índice de documentos (endereço #fiscal, sem aba no menu) | só o índice de documentos, certidões, cadastros e contratos, com validade e link para o original no Drive; o link abre apenas para quem tem acesso ao Drive da TRX |
| Urgente agora | uma linha por frente com o que passou da faixa de parado, só quando a faixa já é tempo real |

**Como a medição funciona.** `scripts/fluxo.py` roda a cada rodada, depois de baixar as planilhas. Ele compara a Fase de cada linha com a da rodada anterior e registra a passagem. A hora exata vem da aba Historico quando a mudança foi feita pelo app de Edição; mudança feita direto na planilha entra com a hora da rodada. O estado mora em três abas da Pipeline Licitações, criadas na primeira rodada:

| Aba | O que guarda |
|---|---|
| `Fluxo_Estado` | uma linha por item: Frente, Chave, Fase, Desde, Fonte e Desde_etapa. É reescrita quando algo muda |
| `Fluxo_Transicoes` | uma linha por passagem de fase: Quando, Frente, Chave, De, Para e Fonte. Só cresce |
| `Fluxo_Fotos` | uma foto por dia: Dia, Frente, Fase e Itens, mais a linha "(em andamento)" de cada frente |

Não edite essas abas à mão. Apagar a `Fluxo_Estado` faz a medição recomeçar, semeada pelo Historico.

**Regras.** `config/fluxo.json` guarda as fases de fila, o limite único por frente, a faixa de dias por etapa, e a regra de revisão do Claude. Enquanto o limite de uma frente está `null`, vale o teto provisório: o que estava em andamento na primeira foto. A faixa de dias é provisória até a etapa ter 8 passagens medidas; daí em diante é o percentil 70 (atenção) e o percentil 85 (parado) do tempo real. A previsão por simulação aparece com 8 semanas de passagens. Mudança de limite ou de faixa passa pelo Marcos.

**Minha fila sem versão nova do app.** A coluna de cada tarefa sai das observações da aba Tarefas_Status: `fazendo`, `a fazer`, `bloqueado: motivo`, `liberado` e `@claude pedido`. A resposta com Autor Claude leva o cartão para Para revisar. O app de Edição v18 já grava tudo isso.

## Segredos necessários (Settings → Secrets and variables → Actions)
- `GOOGLE_SA_JSON`: conteúdo do arquivo JSON da chave da conta de serviço. As planilhas precisam estar compartilhadas com o e-mail dessa conta, como leitor.
- `CENTRAL_SENHA`: senha da equipe (8 caracteres ou mais). Desde 20/10/2026 a página publica só `central.enc`: `dados_central.js`, `saude.js` e `roteiro.js` são cifrados (PBKDF2 + AES-256-GCM, `scripts/cifrar_central.py`) e apagados antes da publicação. A página pede a senha uma vez e a guarda no navegador; o botão Sair apaga. Para trocar a senha: trocar o segredo, rodar o workflow e avisar a equipe. Sem o segredo a rodada falha e nada é publicado.

## O que continua público
O repositório é público: `config/roteiro.json`, `apps-script/Codigo.gs` (com o roteiro embutido), os IDs das planilhas e o `site/index.html` ficam visíveis no GitHub, mesmo com a página cifrada. No `index.html` estão os dados do prestador que saem na nota fiscal (razão social, CNPJ, endereço e conta bancária). Repasse por médico e nomes de radiologistas saíram do código em 17/11/2026 e moram só na planilha; eles continuam no histórico dos commits 6aa177c e 59a1044. Para esconder também isso, o repositório precisa virar privado (GitHub Pages em repositório privado exige plano pago) ou o roteiro precisa sair do repositório.

## Central TRX · Edição (Apps Script)
A pasta `apps-script/` tem o app de edição. É um projeto Apps Script próprio, implantado como app da Web que roda como a conta da TRX (`USER_DEPLOYING`) e aceita acesso anônimo: quem entra se identifica por **apelido + PIN**, validados na coluna PIN da aba Equipe (v12, 12/11/2026). Sem credencial válida nada é lido nem gravado.

| Ação | O que grava | Desde |
|---|---|---|
| edição das frentes | colunas liberadas em `FRENTES` da Pipeline TRX e da Pipeline Licitações; cada mudança vai para a aba Historico | v1 |
| Mural | aba Mural da Pipeline TRX; `@apelido` marca alguém | v13 |
| Feito, Ciente e Observação | aba Tarefas_Status | v14 |
| Objetivos da semana e e-mail para a equipe | abas Objetivos e Emails | v15 |
| `producaoLancar` | aba Producao_Socios (substitui o mês, o contrato e a modalidade; preserva ADM e outros contratos) | v16 |
| `entregaGuardar` | aba Entregas_HRVJ e a linha automática "Produção do HRVJ" do Destaque_ISGH | v17 |
| `entregaGuardar` com `contrato` e `modalidade` | a RM do HRVJ segue na Entregas_HRVJ; os outros hospitais e modalidades vão para a aba Entregas_Geral (criada na primeira gravação), com a linha automática "Produção <SIGLA> <MOD>" no Destaque_ISGH | v18 |
| `producaoLancar` por modalidade | o repasse da TC, do RX e de outras modalidades vem de `repasse_padrao_<MOD>` e `repasse_<MOD>: Nome` da Producao_Params; sem a linha, nada é lançado | v18 |
| `medicaoGravar` | colunas F (laudos de RM) e K (relatório enviado em) da aba Medicoes da planilha Faturamento e Cobranca HRVJ ISGH | v17 |

As três últimas só aceitam os apelidos listados em `producao_lancadores` da Producao_Params (área financeira). Depois de mudar o `Codigo.gs`, é preciso implantar uma versão nova na mesma URL (Implantar → Gerenciar implantações → editar → Nova versão).

## Relatórios (aba nova, 17/11/2026)
A Carla solta na aba **Relatórios** a planilha de apuração que o sistema do hospital exporta e a Central monta o relatório diário e o fechamento para nota fiscal, em A4, para salvar em PDF pela impressão do navegador. O arquivo é lido no navegador com a SheetJS de `site/vendor/xlsx.mini.min.js` e não sai dele.
- **Régua do agrupamento:** dez categorias nomeadas e o resto em Outros. Nome de radiologista não entra no relatório do cliente; prazo não entra em lugar nenhum; o valor unitário aparece uma vez só.
- **Banco de entregas:** a aba `Entregas_HRVJ` da Pipeline Licitações (Emissao, Total, Autor, Quando, Obs). O número em destaque do relatório diário é a diferença contra a última entrega anterior à data de emissão. O botão Guardar como última entrega grava na planilha; o navegador guarda só um cache de 3 horas, até a rodada seguinte trazer a planilha.
- **Produção:** o botão Atualizar a produção manda médico, exames e receita ao app de Edição. O repasse (`repasse_padrao` e linhas `repasse: Nome`) e a marca de sócio (`socio_nomes`) são aplicados pelo app a partir da Producao_Params. **Nenhum valor de repasse nem nome de médico mora no código.** O arquivo tem de ser o acumulado: cada envio substitui o mês inteiro, e a tela avisa quando o arquivo é menor que a última entrega.
- **Cobrança:** o botão Registrar a medição grava F e K na planilha de cobrança, que é o que a tarefa "TRX — Cobrança HRVJ/ISGH" lê.
- **Por hospital (20/11/2026):** a planilha de apuração traz as colunas Instituição e Modalidade. A tela lista os conjuntos hospital + modalidade do arquivo e monta um relatório por vez, cada um com cliente, banco de entregas e produção próprios. Os hospitais conhecidos ficam em `CONTRATOS` no `index.html` (HRVJ, HRI, HUC); instituição desconhecida entra com a sigla do arquivo. A RM do HRVJ continua como antes e aceita o app v17; qualquer outro conjunto só grava com o app v18. A planilha de cobrança só existe para a RM do HRVJ. Angiotomografia de coronárias tem preço próprio: a tela avisa quando o conjunto traz esse exame, porque o fechamento aplica um valor único por laudo.

## Kit (aba nova, 17/11/2026)
Modelos da marca para a equipe: ofício, comunicado, ata, proposta e e-mail, imagem de grupo do WhatsApp e bloco de marca. A fonte do padrão é o artefato Kit de Modelos Corporativos TRX e o design system TRX; os tokens estão copiados no `index.html`, então mudança na marca precisa ser trazida para cá (a tarefa semanal "Design system TRX" confere).

## Início (17/11/2026)
Mural e Objetivos da semana ficam logo abaixo do painel do dia, lado a lado, em cartões maiores. Cada item do Urgente agora abre no próprio Início, com texto, dono e botões para a planilha ou para a aba de origem.
