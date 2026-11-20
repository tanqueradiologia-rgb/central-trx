/**
 * Central TRX · Edição — v18 (20/11/2026): relatório, banco de entregas e produção POR HOSPITAL e
 *   por modalidade. entregaGuardar aceita contrato e modalidade (a RM do HRVJ segue na aba
 *   Entregas_HRVJ; o resto vai para a aba Entregas_Geral, criada na primeira gravação) e
 *   producaoLancar aplica o repasse da modalidade (repasse_padrao_TC, "repasse_TC: Nome").
 *   v17 (17/11/2026): banco de entregas do HRVJ (aba Entregas_HRVJ),
 *   medição na planilha de cobrança e produção restrita a producao_lancadores, com o repasse
 *   lido da Producao_Params. v16: producaoLancar. v15 (17/11/2026): Objetivos da semana (aba Objetivos) e e-mail para a
 *   equipe enviado pela Central (conta da TRX, resposta para quem escreveu; registro na aba Emails).
 *   v14 (16/11/2026): Feito, Ciente e Observação nas tarefas do bloco Hoje
 *   (aba Tarefas_Status na Pipeline TRX). v13 (15/11/2026): Mural da equipe (aba Mural).
 * App web (projeto próprio, separado dos scripts da planilha) que lê e grava na
 * "Pipeline TRX — Prospecção (fonte da verdade)" pelo ID em PLANILHA_ID.
 *
 * A planilha continua sendo a fonte da verdade. Desde a v12 o app roda como a
 * conta da TRX (implantar como "Executar como: eu" e acesso "Qualquer pessoa,
 * inclusive anônima") e quem usa se identifica por APELIDO + PIN, validados na
 * aba Equipe (coluna PIN; Ativo e Edicao diferentes de "não"). Ninguém precisa
 * de login Google, de autorizar o app nem de acesso à planilha. Toda função
 * chamada pela página valida a credencial antes de ler ou gravar; o histórico
 * registra o e-mail da pessoa da aba Equipe como autor.
 *
 * Cada frente é uma entrada em FRENTES: clínicas (Pipeline TRX), licitações e quadro de
 * credenciamento (Pipeline Licitações TRX, aba Licitacoes, separadas pela coluna Trilha).
 * Historico e Equipe ficam sempre na Pipeline TRX, para todas as frentes.
 */

const PLANILHA_ID = '1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0';  // Pipeline TRX — Prospecção (fonte da verdade): clínicas, Historico e Equipe
const LICIT_ID = '1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8';    // Pipeline Licitações TRX (fonte da verdade)

// ROTEIRO-INICIO (gerado por scripts/gerar_roteiro.py a partir de config/roteiro.json: não edite aqui)
const ROTEIRO = {"_sobre":"Fonte única do roteiro comercial da TRX. scripts/gerar_roteiro.py gera site/roteiro.js (Central) e o bloco ROTEIRO do apps-script/Codigo.gs (app de Edição). O roteiro orienta; quem decide é a equipe.","versao":"01/10/2026 · roteiro rev. 26/08/2026 + homologação e implantação","papeis":{"Carla":"Prospecção: pescaria do decisor, cadência de toques, licitações e quadro público.","Gestor":"Gestor do contrato. É papel do contrato, não cargo fixo: cada cliente tem o seu. Hoje são Bruno e Thalyta. Na passagem da linha escolha Gestor Bruno ou Gestora Thalyta, para o aviso chegar só a quem assume; a menção @gestor do contrato continua avisando os dois.","Socios medicos":"Dois sócios médicos na conversa clínica: um traz o dado, o outro guarda o preço.","Marcos":"Monta a proposta com o gestor, decide participação em licitação e assina com o certificado A1.","Bruno Sato":"Sócio médico responsável pelo fechamento: negociação final e assinatura, com liberdade de canal, ritmo e formato.","TI":"Homologação e implantação: integração com o PACS e os sistemas do cliente."},"regras":["Preço só na etapa 4. Quando o número sai antes, a conversa vira comparação de tabela e a TRX perde onde é mais forte, porque a diferença dela é clínica.","A etapa vira com a entrega, não com a impressão. Sem a entrega, o dono anterior continua responsável.","Toda proposta sai com a TRX em cópia, para o grupo acompanhar a negociação sem precisar perguntar.","Os sócios nunca discordam na frente do cliente sobre o valor do serviço."],"particulares":{"titulo":"Clínicas e hospitais particulares","etapas":[{"n":1,"nome":"Pescaria do decisor","dono":"Carla","preco":false,"objetivo":"Encontrar e engajar quem decide de verdade: o radiologista ou o responsável técnico, não só o administrador. A cadência de toques acontece toda aqui.","fecha":"O convite da reunião chega às mãos do gestor do contrato. Até o convite passar, o lead é da Carla."},{"n":2,"nome":"Reunião de diagnóstico","dono":"Gestor","preco":false,"objetivo":"Ouvir a operação do cliente e mapear onde dói: tempo de laudo, plantão descoberto, PACS, fila parada. Sair da reunião com a conversa clínica marcada, com quem decide e, de preferência, com o radiologista.","fecha":"O gestor entrega aos sócios médicos a ata da reunião, com a lista de participantes."},{"n":3,"nome":"Conversa clínica","dono":"Socios medicos","preco":false,"objetivo":"Médico falando com médico sobre o problema clínico. Combinem antes quem faz o quê: um traz o dado (tempo de laudo medido, risco, SLA, LGPD) e o outro guarda o preço. O guardião não diz número.","fecha":"O cliente diz que quer o serviço, ainda sem nenhum número na mesa."},{"n":4,"nome":"Proposta escrita","dono":"Marcos","preco":true,"objetivo":"O preço entra, por escrito. Marcos e gestor montam a proposta, o Marcos manda ao gestor e o gestor encaminha ao cliente.","fecha":"O e-mail com a proposta é enviado ao cliente, com a TRX em cópia."},{"n":5,"nome":"Fechamento","dono":"Bruno Sato","preco":true,"objetivo":"Negociação final e assinatura. O responsável pelo fechamento tem liberdade total de canal, ritmo e formato.","fecha":"O contrato é assinado."},{"n":6,"nome":"Homologação e implantação","dono":"Gestor","preco":true,"objetivo":"Integração com o PACS e os sistemas do cliente, acessos, VPN, testes de laudo e homologação pelo cliente, como no HNSA. O gestor do contrato conduz com a TI.","fecha":"O cliente homologa e o primeiro laudo sai em produção."}],"fases":{"Mapeando":{"e":1,"resp":"Carla","faz":"Conferir se a clínica tem perfil (modalidades, gancho e a Dor medida). Se tiver, passar para Pesquisando decisor."},"Pesquisando decisor":{"e":1,"resp":"Carla","faz":"Achar o radiologista ou o responsável técnico e quem assina contratos (quadro de sócios no CNPJ, site, Instagram, LinkedIn). Preencher Decisor e Cargo e marcar o Início da cadência."},"Em cadencia":{"rot":"Em cadência","e":1,"resp":"Carla","faz":"Rodar os 6 toques em cerca de 21 dias, alternando e-mail, telefone e WhatsApp. A cada contato, atualizar Toque atual e Próximo toque. Nenhum número de preço."},"Decisor engajado":{"e":1,"resp":"Carla","faz":"O decisor topou conversar. Marcar a reunião de diagnóstico e entregar o convite ao gestor do contrato; aí a Fase vira Handoff gestor."},"Handoff gestor":{"e":2,"resp":"Gestor","faz":"Convite nas mãos do gestor. Ele confirma a reunião e lê o histórico da linha (decisor, gancho, notas)."},"Diagnostico operacional":{"rot":"Diagnóstico operacional","e":2,"resp":"Gestor","faz":"Reunião de diagnóstico: tempo de laudo, plantão descoberto, PACS, fila parada. Sair com a conversa clínica marcada e entregar a ata, com participantes, aos sócios médicos."},"Conversa clinica":{"rot":"Conversa clínica","e":3,"resp":"Socios medicos","faz":"Combinar antes quem traz o dado e quem guarda o preço. Ninguém diz número. Termina quando o cliente diz que quer o serviço."},"Proposta escrita":{"e":4,"resp":"Marcos","faz":"Marcos e gestor montam a proposta; o Marcos manda ao gestor e o gestor envia ao cliente, com a TRX em cópia."},"Negociacao":{"rot":"Negociação","e":5,"resp":"Bruno Sato","faz":"Negociação final e assinatura conduzidas pelo Bruno Sato."},"Fechado":{"e":6,"resp":"Gestor","faz":"Contrato assinado. Abrir a homologação e implantação com a TI e registrar o combinado em Resultado."},"Implantacao":{"rot":"Implantação","e":6,"resp":"Gestor","faz":"Integração com o PACS, acessos, testes de laudo e homologação pelo cliente."},"Em operacao":{"rot":"Em operação","e":7,"resp":"Gestor","faz":"Contrato em produção. A gestão do contrato, o faturamento e a distribuição de valores entram numa fase futura da Central."},"Sem retorno":{"e":0,"resp":"Carla","faz":"A cadência terminou sem resposta. Pode voltar à etapa 1 se surgir sinal novo (vaga de radiologista, troca de dono, unidade nova)."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}},"cadencia":[{"n":1,"dia":0,"canal":"E-mail","obj":"Abertura: apresentar a TRX e o gancho específico da clínica."},{"n":2,"dia":2,"canal":"Telefone","obj":"Falar com o decisor ou descobrir quem responde por contratos."},{"n":3,"dia":5,"canal":"WhatsApp","obj":"Mensagem curta de valor, retomando o e-mail."},{"n":4,"dia":9,"canal":"Telefone","obj":"Nova tentativa, em horário ou turno diferente."},{"n":5,"dia":14,"canal":"WhatsApp","obj":"Benefícios concretos e convite para 15 minutos de conversa."},{"n":6,"dia":21,"canal":"E-mail","obj":"Encerramento educado, deixando a porta aberta."}]},"licitacoes":{"titulo":"Licitações, credenciamentos e pregões","aviso":"No público o caminho é o edital: não há cadência nem conversa de preço antes da disputa. Mapa proposto pelo Claude a partir do que já funciona; ajuste com o Marcos.","etapas":[{"n":1,"nome":"Triagem","dono":"Carla","preco":false,"objetivo":"Ler o resumo, conferir no mesmo dia o cadastro na plataforma da disputa (a TRX já perdeu processos por cadastro) e anotar travas: alvara sanitario, presencial, atestado, exclusividade ME/EPP. CNES nao e trava: a TRX tem CNES 8596204 desde 25/10/2026 e anexa a ficha.","fecha":"O Marcos decide participar, ou a linha vai para Descartado com o motivo em Resultado."},{"n":2,"nome":"Edital e habilitação","dono":"Carla","preco":false,"objetivo":"Fase Montando habilitacao: a pasta do processo e o checklist saem sozinhos. A Carla adapta as declarações e o Marcos assina com o certificado A1.","fecha":"Documentos e proposta enviados na plataforma dentro do prazo."},{"n":3,"nome":"Disputa e julgamento","dono":"Marcos","preco":true,"objetivo":"A Carla acompanha a sessão e as diligências. O Marcos define o lance, nunca abaixo do piso, e responde recursos.","fecha":"Resultado publicado: habilitado, credenciado, ganho ou perdido."},{"n":4,"nome":"Contrato","dono":"Marcos","preco":true,"objetivo":"Assinar o contrato ou o termo de credenciamento e definir o gestor do contrato.","fecha":"Contrato ou termo assinado e gestor definido."},{"n":5,"nome":"Homologação e implantação","dono":"Gestor","preco":true,"objetivo":"Integração com o PACS e os sistemas do órgão, acessos, testes de laudo e homologação, como no HNSA.","fecha":"Primeiro laudo em produção."}],"fases":{"Mapeado":{"e":1,"resp":"Carla","faz":"Ler o resumo, conferir o cadastro na plataforma hoje e levar ao Marcos a decisão de participar."},"Lendo edital":{"e":1,"resp":"Carla","faz":"Levantar exigências e travas (alvará sanitário, presencial, atestado, índices, ME/EPP, preço por laudo contra o piso) e registrar em Trava. CNES não entra: a TRX tem CNES 8596204 desde 25/10/2026."},"Montando habilitacao":{"rot":"Montando habilitação","e":2,"resp":"Carla","faz":"A pasta e o checklist saem sozinhos. Adaptar as declarações e separar o que o Marcos assina com o A1."},"Documentos enviados":{"e":3,"resp":"Carla","faz":"Acompanhar a plataforma e responder diligências no prazo."},"Proposta enviada":{"e":3,"resp":"Carla","faz":"Acompanhar a sessão. Lance só com o Marcos e nunca abaixo do piso."},"Em analise":{"rot":"Em análise","e":3,"resp":"Carla","faz":"Acompanhar a análise e responder diligências."},"Em julgamento":{"e":3,"resp":"Marcos","faz":"Acompanhar o julgamento e decidir sobre recurso."},"Habilitado":{"e":4,"resp":"Marcos","faz":"Aguardar a homologação e preparar a assinatura."},"Credenciado":{"e":4,"resp":"Marcos","faz":"Assinar o termo e definir o gestor do contrato."},"Ganho":{"e":4,"resp":"Marcos","faz":"Assinar o contrato e definir o gestor do contrato."},"Implantacao":{"rot":"Implantação","e":5,"resp":"Gestor","faz":"Integração com o PACS, acessos, testes de laudo e homologação pelo órgão."},"Em operacao":{"rot":"Em operação","e":6,"resp":"Gestor","faz":"Contrato em produção. Gestão, faturamento e distribuição de valores entram numa fase futura."},"Perdido":{"e":0,"resp":"Carla","faz":"Registrar em Resultado por que perdemos (preço, documentação, cadastro, prazo)."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}}},"quadro":{"titulo":"Quadro público (municípios sem processo aberto)","aviso":"Prospecção ativa no público: o objetivo é fazer o órgão abrir credenciamento. Quando abrir, a linha vira processo na aba Licitações.","etapas":[{"n":1,"nome":"Contato com o órgão","dono":"Carla","preco":false,"objetivo":"Achar o secretário de saúde, o diretor da unidade ou o consórcio (CIS) e enviar a apresentação com o pacote de habilitação.","fecha":"O órgão responde."},{"n":2,"nome":"Reunião com o órgão","dono":"Gestor","preco":false,"objetivo":"Apresentar a TRX e entender volume, equipamentos e a forma de contratar (credenciamento, dispensa, adesão a ata).","fecha":"O órgão abre o processo; a linha passa para Licitações."}],"fases":{"Em aberto":{"e":1,"resp":"Carla","faz":"Achar o contato certo e enviar a apresentação."},"E-mail enviado":{"e":1,"resp":"Carla","faz":"Retomar em cerca de 7 dias por telefone ou WhatsApp."},"Documentos enviados":{"e":1,"resp":"Carla","faz":"Confirmar o recebimento e perguntar se pretendem abrir credenciamento."},"Respondeu":{"e":2,"resp":"Carla","faz":"Marcar a reunião e entregar o convite ao gestor."},"Reuniao marcada":{"rot":"Reunião marcada","e":2,"resp":"Gestor","faz":"Reunião com o órgão: volume, equipamentos e forma de contratação."},"Sem interesse":{"e":0,"resp":"","faz":"Registrar o motivo em Resultado."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}}}};
// ROTEIRO-FIM

// Fases e responsáveis seguem o roteiro comercial (config/roteiro.json). A validação da planilha usa as mesmas listas.
const FASES_CLINICA = Object.keys(ROTEIRO.particulares.fases);
// 'Gestor' virou dois papeis nominais em 06/11/2026 (pedido da Carla): a passagem da linha avisa
// so quem assume. O papel coletivo 'Gestor' continua na aba Equipe e na mencao @gestor do contrato.
const RESP_CLINICA = ['Carla', 'Gestor Bruno', 'Gestora Thalyta', 'Socios medicos', 'Marcos', 'Bruno Sato', 'TI'];
const FASES_PROCESSO = ['Mapeado', 'Lendo edital', 'Montando habilitacao', 'Documentos enviados', 'Proposta enviada',
  'Em analise', 'Em julgamento', 'Habilitado', 'Credenciado', 'Ganho', 'Implantacao', 'Em operacao', 'Perdido', 'Descartado'];
const FASES_SEM_PROCESSO = ['Em aberto', 'E-mail enviado', 'Documentos enviados', 'Respondeu', 'Reuniao marcada',
  'Sem interesse', 'Descartado'];
const ENVIO = ['Aguardando envio', 'Sem e-mail (achar contato)', 'Rascunho gerado', 'E-mail enviado',
  'Documentos enviados', 'Respondeu', 'Reenviar'];

const LEITURA_LIC = ['ID', 'Trilha', 'Fase', 'Situacao do envio', 'Encaixe', 'Score', 'Faixa', 'Dor', 'Prazo', 'Dias',
  'Orgao', 'Cidade', 'UF', 'Modalidade', 'Edital', 'Objeto', 'Valor estimado', 'Onde disputa', 'Bloqueio', 'Contato',
  'Cargo', 'Telefone', 'WhatsApp', 'E-mail', 'Proxima acao', 'Quando', 'Responsavel', 'Notas da Carla', 'Resultado',
  'Link edital', 'Link PNCP', 'Origem', 'Atualizado em'];

function doQuadro_(r) { return String(r.Origem || '').indexOf('Quadro') === 0 && !String(r.Edital || '').trim(); }

const FRENTES = {
  clinicas: {
    titulo: 'Clínicas particulares',
    planilha: PLANILHA_ID,
    aba: 'Pipeline',
    chave: 'Clinica',            // coluna que identifica a linha
    chave2: 'Cidade',            // desempate quando há nomes repetidos
    // colunas mostradas na lista e no detalhe (só leitura)
    leitura: ['Clinica', 'Cidade', 'UF', 'Prioridade', 'Modalidades', 'Gancho', 'Responsavel', 'Fase',
      'Decisor', 'Cargo', 'Telefone', 'WhatsApp', 'Email', 'LinkedIn', 'Toque_atual', 'Inicio_cadencia', 'Proximo_toque', 'Ultima_atualizacao',
      'Resultado', 'Notas', 'Proxima_Acao', 'Score', 'Faixa', 'Dor', 'Cobertura', 'Janela',
      'Sinal_de_compra', 'Necessidade', 'Sinal_operacional', 'Nota_RA', 'O_que_reclamam', 'Medido_em'],
    // colunas que a equipe pode mudar pelo app
    edicao: {
      Fase: { tipo: 'lista', opcoes: FASES_CLINICA },
      Responsavel: { tipo: 'lista', opcoes: RESP_CLINICA },
      Proxima_Acao: { tipo: 'texto' },
      Inicio_cadencia: { tipo: 'data' },
      Toque_atual: { tipo: 'lista', opcoes: ['', '0', '1', '2', '3', '4', '5', '6'] },
      Proximo_toque: { tipo: 'data' },
      Resultado: { tipo: 'texto' },
      Decisor: { tipo: 'texto' },
      Cargo: { tipo: 'texto' },
      Telefone: { tipo: 'tel' },
      WhatsApp: { tipo: 'whats' },
      Email: { tipo: 'email' }
    },
    carimbo: 'Ultima_atualizacao'   // gravado com a data de hoje a cada edição
  },
  licitacoes: {
    titulo: 'Licitações e credenciamentos',
    planilha: LICIT_ID,
    aba: 'Licitacoes',
    chave: 'ID',
    filtro: function (r) {
      if (r.Trilha === 'CREDENCIAMENTO' || r.Trilha === 'PREGAO' || r.Trilha === 'ENCERRADO') return true;
      return r.Trilha === 'DESCARTADOS' && !doQuadro_(r);
    },
    leitura: LEITURA_LIC,
    edicao: {
      Fase: { tipo: 'lista', opcoes: FASES_PROCESSO },
      Responsavel: { tipo: 'equipe' },
      'Proxima acao': { tipo: 'texto' },
      Quando: { tipo: 'data' },
      Contato: { tipo: 'texto' },
      Cargo: { tipo: 'texto' },
      Telefone: { tipo: 'tel' },
      WhatsApp: { tipo: 'whats' },
      'E-mail': { tipo: 'email' },
      Resultado: { tipo: 'texto' }
    }
  },
  quadro: {
    titulo: 'Quadro de credenciamento (municípios sem processo aberto)',
    planilha: LICIT_ID,
    aba: 'Licitacoes',
    chave: 'ID',
    filtro: function (r) {
      if (r.Trilha === 'SEM PROCESSO') return true;
      return r.Trilha === 'DESCARTADOS' && doQuadro_(r);
    },
    leitura: LEITURA_LIC,
    edicao: {
      Fase: { tipo: 'lista', opcoes: FASES_SEM_PROCESSO },
      'Situacao do envio': { tipo: 'lista', opcoes: ENVIO },
      Responsavel: { tipo: 'equipe' },
      'Proxima acao': { tipo: 'texto' },
      Quando: { tipo: 'data' },
      Contato: { tipo: 'texto' },
      Cargo: { tipo: 'texto' },
      Telefone: { tipo: 'tel' },
      WhatsApp: { tipo: 'whats' },
      'E-mail': { tipo: 'email' },
      Resultado: { tipo: 'texto' }
    }
  }
};

const ABA_HIST = 'Historico';
const ABA_EQUIPE = 'Equipe';
const TZ = 'America/Sao_Paulo';

/** Credencial apelido + PIN contra a aba Equipe. Entra quem tem PIN preenchido,
 *  Ativo diferente de "não" e Edicao diferente de "não". Devolve a pessoa ou null.
 *  Sem Session.getActiveUser(): com o app rodando como a conta da TRX, o login
 *  Google de quem acessa não identifica ninguém. */
function validar_(cred) {
  const a = String(cred && cred.apelido || '').trim().toLowerCase();
  const p = String(cred && cred.pin || '').trim();
  if (!a || !p) return null;
  return equipeComPin_().filter(function (q) {
    return q.apelido === a && q.edicao && q.pin && q.pin === p;
  })[0] || null;
}

/** Toda função chamada pela página começa por aqui. A página serve a qualquer um;
 *  os dados, não: sem credencial válida nada é lido nem gravado. */
function exigir_(cred) {
  const eu = validar_(cred);
  if (!eu) throw new Error('LOGIN: apelido ou PIN não conferem. Confira com o Marcos o seu PIN na aba Equipe.');
  return eu;
}

function doGet(e) {
  // A página abre para qualquer um e pede apelido + PIN; sem credencial válida nenhum dado sai.
  // Link vindo da Central (GitHub): ?f=clinicas|licitacoes|quadro&l=<linha da planilha> abre a linha direto.
  const t = HtmlService.createTemplateFromFile('Index');
  const p = (e && e.parameter) || {};
  t.abrirFrente = /^(clinicas|licitacoes|quadro)$/.test(p.f || '') ? p.f : '';
  t.abrirLinha = /^\d{1,6}$/.test(p.l || '') ? p.l : '';
  return t.evaluate()
    .setTitle('Central TRX · Edição')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** API JSON do mural para a Central (GitHub Pages), v13.1 de 15/11/2026.
 *  A Central posta por fetch(EDIT_URL, {method:'POST', body: JSON com action/cred/msg}).
 *  Mesma regra de sempre: nada é lido nem gravado sem apelido+PIN válidos. */
function doPost(e) {
  let out;
  try {
    const p = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (p.action === 'muralGet') out = muralGet(p.cred);
    else if (p.action === 'muralPostar') out = muralPostar(p.cred, p.msg);
    else if (p.action === 'tarefaMarcar') out = tarefaMarcar(p.cred, p.t);
    else if (p.action === 'objetivoNovo') out = objetivoNovo(p.cred, p.o);
    else if (p.action === 'objetivoMarcar') out = objetivoMarcar(p.cred, p.o);
    else if (p.action === 'emailEnviar') out = emailEnviar(p.cred, p.m);
    else if (p.action === 'producaoLancar') out = producaoLancar(p.cred, p.dados);
    else if (p.action === 'versao') out = { versao: 18 };
    else if (p.action === 'entregaGuardar') out = entregaGuardar(p.cred, p.e);
    else if (p.action === 'medicaoGravar') out = medicaoGravar(p.cred, p.m);
    else throw new Error('Ação desconhecida.');
    out.ok = true;
  } catch (err) {
    out = { ok: false, erro: String((err && err.message) || err) };
  }
  return ContentService.createTextOutput(JSON.stringify(out))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ---------------- leitura ---------------- */

function planilha_(id) { return SpreadsheetApp.openById(id || PLANILHA_ID); }

function cabecalho_(sh) {
  const h = sh.getRange(1, 1, 1, sh.getLastColumn()).getDisplayValues()[0];
  const idx = {};
  h.forEach(function (n, i) { if (n) idx[String(n).trim()] = i; });
  return idx;
}

/** "não" em qualquer grafia (nao, Não, NAO). Em branco nunca é não. */
function ehNao_(v) {
  const t = String(v == null ? '' : v).trim().toLowerCase();
  return t === 'não' || t === 'nao';
}

/** Aba Equipe, colunas lidas pelo cabeçalho: Nome | Email | Apelido | Ativo | Papel | ... | Edicao | PIN.
 *  Ativo = está na equipe (menções, papéis e avisos). Edicao = entra no app de Edição.
 *  PIN = credencial de entrada no app (v12); sem PIN a pessoa não entra. */
function equipeComPin_() {
  const sh = planilha_().getSheetByName(ABA_EQUIPE);
  if (!sh || sh.getLastRow() < 2) return [];
  const idx = cabecalho_(sh);
  const col = function (r, nome, padrao) {
    const i = idx[nome];
    return i === undefined ? (padrao === undefined ? '' : padrao) : r[i];
  };
  return sh.getRange(2, 1, sh.getLastRow() - 1, sh.getLastColumn()).getDisplayValues()
    .filter(function (r) { return col(r, 'Nome') && !ehNao_(col(r, 'Ativo')); })
    .map(function (r) {
      const nome = col(r, 'Nome');
      return { nome: nome, email: String(col(r, 'Email') || '').trim(),
        apelido: String(col(r, 'Apelido') || nome).toLowerCase(),
        edicao: !ehNao_(col(r, 'Edicao')),
        pin: String(col(r, 'PIN') || '').trim(),
        papeis: String(col(r, 'Papel') || '').split(',').map(function (x) { return x.trim(); }).filter(String) };
    });
}

/** A mesma lista SEM o PIN: é a que vai para a página. O PIN nunca sai do servidor. */
function equipe_() {
  return equipeComPin_().map(function (p) {
    return { nome: p.nome, email: p.email, apelido: p.apelido, edicao: p.edicao, papeis: p.papeis };
  });
}

/** Quem recebe aviso quando uma linha passa para "quem": nome da pessoa ou papel do roteiro (Gestor, Socios medicos...). */
function emailsDe_(quem, eq) {
  const q = String(quem || '').trim().toLowerCase();
  if (!q) return [];
  return eq.filter(function (e) {
    return e.email && (e.nome.toLowerCase() === q || e.apelido === q ||
      e.papeis.some(function (p) { return p.toLowerCase() === q; }));
  }).map(function (e) { return e.email; });
}

/** Menções e passagens dos últimos 30 dias para o e-mail da pessoa logada.
 *  O "lido até quando" vive no navegador de cada um desde a v12 (sem conta Google
 *  não há UserProperties por pessoa): a página marca os novos pelo campo t. */
function getAvisos_(eu) {
  eu = String(eu || '').toLowerCase();
  const sh = planilha_().getSheetByName(ABA_HIST);
  if (!eu || !sh || sh.getLastRow() < 2) return { avisos: [] };
  const ini = Math.max(2, sh.getLastRow() - 3000);
  const vals = sh.getRange(ini, 1, sh.getLastRow() - ini + 1, 10).getValues();
  const limite = Date.now() - 30 * 864e5;
  const out = [];
  vals.forEach(function (r) {
    const menc = String(r[9] || '').toLowerCase();
    if (menc.indexOf(eu) < 0) return;
    const quando = r[0] instanceof Date ? r[0] : parseBr_(r[0]);
    const t = quando ? quando.getTime() : 0;
    if (t && t < limite) return;
    const tipo = String(r[4] || '');
    out.push({ quando: quando ? Utilities.formatDate(quando, TZ, 'dd/MM HH:mm') : String(r[0]), t: t,
      autor: r[1], linha: r[2], nome: r[3], frente: tipo.indexOf(':') > 0 ? tipo.split(':')[0] : 'clinicas',
      tipo: tipo.replace(/^[^:]+:/, ''), msg: r[8] });
  });
  out.sort(function (a, b) { return b.t - a.t; });
  return { avisos: out.slice(0, 60) };
}

function parseBr_(v) {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?/.exec(String(v || ''));
  return m ? new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0)) : null;
}

function historico_(frente) {
  const sh = planilha_().getSheetByName(ABA_HIST);
  const porChave = {};
  if (!sh || sh.getLastRow() < 2) return porChave;
  const vals = sh.getRange(2, 1, sh.getLastRow() - 1, 10).getDisplayValues();
  vals.forEach(function (r) {
    const [quando, autor, linha, nome, tipo, campo, de, para, msg, menc] = r;
    if (tipo.indexOf(frente + ':') !== 0 && !(frente === 'clinicas' && tipo.indexOf(':') < 0)) return;
    const k = nome;
    (porChave[k] = porChave[k] || []).push({ quando: quando, autor: autor, tipo: tipo.replace(/^[^:]+:/, ''), campo: campo, de: de, para: para, msg: msg, menc: menc });
  });
  return porChave;
}

/** Tudo o que a página precisa para abrir. Exige a credencial apelido + PIN. */
function getDados(frente, cred) {
  const eu = exigir_(cred);
  frente = frente || 'clinicas';
  const cfg = FRENTES[frente];
  if (!cfg) throw new Error('Frente desconhecida: ' + frente);
  const ss = planilha_(cfg.planilha);
  const sh = ss.getSheetByName(cfg.aba);
  const idx = cabecalho_(sh);
  const n = sh.getLastRow() - 1;
  const vals = n > 0 ? sh.getRange(2, 1, n, sh.getLastColumn()).getDisplayValues() : [];
  const cols = cfg.leitura.filter(function (c) { return idx[c] !== undefined; });
  const linhas = [];
  vals.forEach(function (r, i) {
    if (!String(r[idx[cfg.chave]] || '').trim()) return;
    const o = { _l: i + 2, _k: r[idx[cfg.chave]] + (cfg.chave2 ? ' · ' + r[idx[cfg.chave2]] : '') };
    cols.forEach(function (c) { o[c] = r[idx[c]]; });
    if (cfg.filtro && !cfg.filtro(o)) return;
    linhas.push(o);
  });
  const hist = historico_(frente);
  return {
    frente: frente,
    titulo: cfg.titulo,
    usuario: eu.email || '',
    usuarioNome: eu.nome || '',
    avisos: getAvisos_(eu.email),
    agora: Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd'T'HH:mm"),
    edicao: cfg.edicao,
    roteiro: ROTEIRO[{ clinicas: 'particulares', licitacoes: 'licitacoes', quadro: 'quadro' }[frente]],
    regras: ROTEIRO.regras,
    equipe: equipe_(),
    linhas: linhas,
    historico: hist,
    frentes: Object.keys(FRENTES).map(function (k) { return { id: k, titulo: FRENTES[k].titulo }; }),
    planilha: ss.getUrl(),
    gid: sh.getSheetId()
  };
}

/* ---------------- gravação ---------------- */

/**
 * pedido = { frente, linha, chave, chave2, campos: {Coluna: valor}, nota, mencoes: [email] }
 * Confere se a linha ainda é a mesma clínica antes de gravar.
 */
function salvar(pedido) {
  const eu = exigir_(pedido && pedido.cred);
  pedido.frente = pedido.frente || 'clinicas';
  const cfg = FRENTES[pedido.frente];
  if (!cfg) throw new Error('Frente desconhecida.');
  const lock = LockService.getScriptLock();   // projeto separado: getDocumentLock() devolve null fora da planilha
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  try {
    const ss = planilha_(cfg.planilha);
    const sh = ss.getSheetByName(cfg.aba);
    const idx = cabecalho_(sh);
    let linha = localizar_(sh, idx, cfg, pedido);
    const larg = sh.getLastColumn();
    const atual = sh.getRange(linha, 1, 1, larg).getDisplayValues()[0];
    const autor = eu.email || eu.nome;   // v12: autoria pela aba Equipe, não pelo login Google
    const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
    // identificação usada no histórico: "Clínica · Cidade" (há nomes repetidos em cidades diferentes)
    const nome = atual[idx[cfg.chave]] + (cfg.chave2 ? ' · ' + atual[idx[cfg.chave2]] : '');
    const hist = [];
    let mudou = false;

    Object.keys(pedido.campos || {}).forEach(function (c) {
      if (!cfg.edicao[c] || idx[c] === undefined) return;       // só colunas liberadas
      const tipo = cfg.edicao[c].tipo;
      let novo = String(pedido.campos[c] == null ? '' : pedido.campos[c]).trim();
      if (tipo === 'whats' && novo) {           // WhatsApp só com dígitos e o 55 do Brasil
        novo = novo.replace(/\D/g, '');
        if (novo.length === 10 || novo.length === 11) novo = '55' + novo;
        if (novo.length < 12 || novo.length > 13) throw new Error('WhatsApp inválido: use DDD e número, ex.: (62) 99430-7537');
      }
      if (tipo === 'email' && novo) {
        novo = novo.toLowerCase();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(novo)) throw new Error('E-mail inválido: ' + novo);
      }
      const velho = String(atual[idx[c]] || '').trim();
      if (novo === velho) return;
      if (tipo === 'lista' && novo && cfg.edicao[c].opcoes.indexOf(novo) < 0)
        throw new Error('Valor inválido para ' + c + ': ' + novo);
      const cel = sh.getRange(linha, idx[c] + 1);
      if (tipo === 'whats' || tipo === 'tel') cel.setNumberFormat('@');   // não vira número nem perde o zero
      cel.setValue(novo);
      hist.push([agora, autor, linha, nome, pedido.frente + ':mudança', c, velho, novo, '', '']);
      mudou = true;
    });

    const nota = String(pedido.nota || '').trim();
    const eq = equipe_();
    // menção a um papel (ex.: "papel:Gestor") vale para todos que têm esse papel na aba Equipe
    let menc = [];
    (pedido.mencoes || []).filter(String).forEach(function (m) {
      (m.indexOf('papel:') === 0 ? emailsDe_(m.slice(6), eq) : [m]).forEach(function (x) { if (menc.indexOf(x) < 0) menc.push(x); });
    });
    menc = menc.filter(function (x) { return x.toLowerCase() !== autor.toLowerCase(); });
    // passagem: quem passa a ser Responsável pela linha é avisado no app e por e-mail
    let passagem = null;
    if (pedido.campos && cfg.edicao.Responsavel && idx.Responsavel !== undefined) {
      const novoResp = String(pedido.campos.Responsavel || '').trim();
      // início do circuito (etapa 1 do roteiro, que já nasce com a Carla): passar para a Carla não gera aviso,
      // senão ela recebe um aviso por linha nova e se perde (decisão do Marcos, 01/10/2026)
      const faseNova = String((pedido.campos.Fase || atual[idx.Fase]) || '').trim();
      const rot = ROTEIRO[{ clinicas: 'particulares', licitacoes: 'licitacoes', quadro: 'quadro' }[pedido.frente]];
      const etapa = rot && rot.fases[faseNova] ? rot.fases[faseNova].e : 0;
      const inicioDaCarla = novoResp.toLowerCase() === 'carla' && etapa <= 1;
      if (novoResp && !inicioDaCarla && novoResp !== String(atual[idx.Responsavel] || '').trim()) {
        const para = emailsDe_(novoResp, eq).filter(function (x) { return x.toLowerCase() !== autor.toLowerCase(); });
        if (para.length) passagem = { para: para, quem: novoResp,
          fase: String((pedido.campos.Fase || atual[idx.Fase]) || '') };
      }
    }
    if (passagem) hist.push([agora, autor, linha, nome, pedido.frente + ':passagem', 'Responsavel', '', passagem.quem,
      'A linha passou para ' + passagem.quem + (passagem.fase ? ' (Fase ' + passagem.fase + ')' : '') + '.', passagem.para.join(', ')]);
    if (nota) {
      hist.push([agora, autor, linha, nome, pedido.frente + ':nota', '', '', '', nota, menc.join(', ')]);
      mudou = true;
    }
    if (!mudou && !passagem) return { ok: true, nada: true };

    if (cfg.carimbo && idx[cfg.carimbo] !== undefined)
      sh.getRange(linha, idx[cfg.carimbo] + 1).setValue(Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd'));

    const hs = planilha_().getSheetByName(ABA_HIST);
    hs.getRange(hs.getLastRow() + 1, 1, hist.length, 10).setValues(hist);
    SpreadsheetApp.flush();

    if (nota && menc.length) avisar_(menc, autor, nome, nota, linha, cfg, pedido.frente);
    if (passagem) avisar_(passagem.para, autor, nome, 'Esta linha passou para ' + passagem.quem +
      (passagem.fase ? ', na Fase ' + passagem.fase : '') + '. Abra para ver o histórico e o próximo passo do roteiro.', linha, cfg, pedido.frente, true);
    return { ok: true, linha: linha, historico: hist.length };
  } finally {
    lock.releaseLock();
  }
}

function localizar_(sh, idx, cfg, pedido) {
  const ultima = sh.getLastRow();
  const ok = function (l) {
    if (l < 2 || l > ultima) return false;
    const r = sh.getRange(l, 1, 1, sh.getLastColumn()).getDisplayValues()[0];
    return r[idx[cfg.chave]] === pedido.chave && (!cfg.chave2 || r[idx[cfg.chave2]] === pedido.chave2);
  };
  if (ok(pedido.linha)) return pedido.linha;
  // a planilha foi reordenada: procura pela chave
  const col = sh.getRange(2, idx[cfg.chave] + 1, ultima - 1, 1).getDisplayValues();
  const col2 = cfg.chave2 ? sh.getRange(2, idx[cfg.chave2] + 1, ultima - 1, 1).getDisplayValues() : null;
  for (let i = 0; i < col.length; i++) {
    if (col[i][0] === pedido.chave && (!col2 || col2[i][0] === pedido.chave2)) return i + 2;
  }
  throw new Error('Não encontrei "' + pedido.chave + '" na planilha. Ela pode ter sido renomeada. Recarregue a página.');
}

function avisar_(emails, autor, nome, nota, linha, cfg, frente, passagem) {
  const url = ScriptApp.getService().getUrl() + '?f=' + (frente || 'clinicas') + '&l=' + linha;
  emails.forEach(function (e) {
    try {
      MailApp.sendEmail({
        to: e,
        subject: 'Central TRX: ' + (passagem ? 'passou para você: ' : 'nota em ') + nome,
        htmlBody: '<p><b>' + autor + '</b> ' + (passagem ? 'passou para você' : 'marcou você numa nota sobre') + ' <b>' + nome + '</b>:</p>' +
          '<blockquote>' + nota.replace(/</g, '&lt;') + '</blockquote>' +
          '<p><a href="' + url + '">Abrir a Central TRX · Edição</a> (' + cfg.titulo + ', linha ' + linha + ' da aba ' + cfg.aba + ').</p>'
      });
    } catch (err) { console.warn('Aviso não enviado para ' + e + ': ' + err); }
  });
}

/* ---------------- mural da equipe (v13, 15/11/2026) ---------------- */

const ABA_MURAL = 'Mural';

function muralAba_() {
  const ss = planilha_();
  let sh = ss.getSheetByName(ABA_MURAL);
  if (!sh) {
    sh = ss.insertSheet(ABA_MURAL);
    sh.getRange(1, 1, 1, 4).setValues([['Quando', 'Autor', 'Mensagem', 'Mencoes']]);
  }
  return sh;
}

function muralLer_() {
  const sh = muralAba_();
  if (sh.getLastRow() < 2) return [];
  const ini = Math.max(2, sh.getLastRow() - 199);
  const vals = sh.getRange(ini, 1, sh.getLastRow() - ini + 1, 4).getDisplayValues();
  return vals.map(function (r) { return { quando: r[0], autor: r[1], msg: r[2], menc: r[3] }; }).reverse();
}

/** Mural da equipe: as últimas 200 mensagens, mais novas primeiro. */
function muralGet(cred) {
  exigir_(cred);
  return { mural: muralLer_() };
}

/** Posta no mural. @apelido no texto vira menção (a Central avisa no zap quando ativo). */
function muralPostar(cred, msg) {
  const eu = exigir_(cred);
  msg = String(msg || '').trim();
  if (!msg) throw new Error('Escreva a mensagem.');
  if (msg.length > 1000) throw new Error('Mensagem longa demais (máximo 1000 caracteres).');
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  try {
    const aps = equipeComPin_().map(function (q) { return q.apelido; });
    const menc = (msg.match(/@[a-z0-9]+/gi) || []).map(function (m) { return m.slice(1).toLowerCase(); })
      .filter(function (a, i, arr) { return aps.indexOf(a) >= 0 && arr.indexOf(a) === i; }).join(', ');
    const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
    muralAba_().appendRow([agora, eu.nome || eu.email, msg, menc]);
  } finally { lock.releaseLock(); }
  return { mural: muralLer_() };
}

/* ---------------- tarefas do bloco Hoje (v14, 16/11/2026) ----------------
 * Cada tarefa da fila de uma pessoa na Central ganha Feito, Ciente e Observação.
 * Uma linha por marcação na aba Tarefas_Status (nada é apagado: é o histórico).
 * Feito ou Ciente tira a tarefa da fila daquela pessoa; observação sozinha não tira,
 * fica visível embaixo da tarefa para quem olhar a fila. A Chave vem da Central
 * (origem + título + prazo + ação): se o prazo ou a ação mudar, a tarefa volta. */

const ABA_TAREFAS = 'Tarefas_Status';
const CAB_TAREFAS = ['Quando', 'Autor', 'Pessoa', 'Chave', 'Tarefa', 'Origem', 'Status', 'Observacao'];

function tarefasAba_() {
  const ss = planilha_();
  let sh = ss.getSheetByName(ABA_TAREFAS);
  if (!sh) {
    sh = ss.insertSheet(ABA_TAREFAS);
    sh.getRange(1, 1, 1, CAB_TAREFAS.length).setValues([CAB_TAREFAS]);
    sh.setFrozenRows(1);
  }
  return sh;
}

function tarefaMarcar(cred, t) {
  const eu = exigir_(cred);
  t = t || {};
  const st = String(t.status || '').trim().toLowerCase();
  if (st && st !== 'feito' && st !== 'ciente') throw new Error('Status inválido.');
  const obs = String(t.obs || '').trim();
  if (!st && !obs) throw new Error('Marque Feito ou Ciente, ou escreva uma observação.');
  if (obs.length > 600) throw new Error('Observação longa demais (máximo 600 caracteres).');
  const chave = String(t.chave || '').trim(), pessoa = String(t.pessoa || '').trim();
  if (!chave || !pessoa) throw new Error('Tarefa sem identificação.');
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
  try {
    tarefasAba_().appendRow([agora, eu.nome || eu.email, pessoa.slice(0, 60), chave.slice(0, 80),
      String(t.titulo || '').slice(0, 200), String(t.origem || '').slice(0, 40), st, obs]);
  } finally { lock.releaseLock(); }
  return { quando: agora, autor: eu.nome || eu.email };
}

/* ---------------- objetivos da semana (v15, 17/11/2026) ----------------
 * Aba Objetivos da Pipeline TRX, uma linha por objetivo. Qualquer pessoa da equipe com
 * apelido + PIN propõe um objetivo para a semana (com dono) e marca Feito ou Não deu,
 * com observação. Semana = data da segunda-feira (dd/MM/yyyy). A Central mostra a semana
 * corrente e o que ficou aberto das anteriores. */

const ABA_OBJ = 'Objetivos';
const CAB_OBJ = ['Semana', 'Objetivo', 'Dono', 'Status', 'Criado', 'Autor', 'Atualizado', 'Observacao'];

function objetivosAba_() {
  const ss = planilha_();
  let sh = ss.getSheetByName(ABA_OBJ);
  if (!sh) {
    sh = ss.insertSheet(ABA_OBJ);
    sh.getRange(1, 1, 1, CAB_OBJ.length).setValues([CAB_OBJ]);
    sh.setFrozenRows(1);
  }
  return sh;
}

function segunda_(d) {
  const x = new Date(d.getTime());
  const dw = (Number(Utilities.formatDate(x, TZ, 'u')) + 6) % 7;   // segunda = 0
  x.setDate(x.getDate() - dw);
  return Utilities.formatDate(x, TZ, 'dd/MM/yyyy');
}

function objetivosLer_() {
  const sh = objetivosAba_();
  if (sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, CAB_OBJ.length).getDisplayValues()
    .map(function (r, i) { return { l: i + 2, sem: r[0], t: r[1], dono: r[2], st: r[3], a: r[5], q: r[6] || r[4], obs: r[7] }; })
    .filter(function (o) { return o.t; });
}

function objetivoNovo(cred, o) {
  const eu = exigir_(cred);
  o = o || {};
  const t = String(o.objetivo || '').trim(), dono = String(o.dono || '').trim();
  if (!t) throw new Error('Escreva o objetivo.');
  if (t.length > 300) throw new Error('Objetivo longo demais (máximo 300 caracteres).');
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
  try {
    objetivosAba_().appendRow([segunda_(new Date()), t, dono.slice(0, 60) || (eu.nome || eu.email), 'aberto', agora, eu.nome || eu.email, '', '']);
  } finally { lock.releaseLock(); }
  return { objetivos: objetivosLer_() };
}

function objetivoMarcar(cred, o) {
  const eu = exigir_(cred);
  o = o || {};
  const st = String(o.status || '').trim().toLowerCase();
  if (['aberto', 'feito', 'nao deu'].indexOf(st) < 0) throw new Error('Status inválido.');
  const l = Number(o.linha), obs = String(o.obs || '').trim().slice(0, 400);
  const sh = objetivosAba_();
  if (!(l >= 2 && l <= sh.getLastRow())) throw new Error('Objetivo não encontrado.');
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
  try {
    const atual = sh.getRange(l, 1, 1, CAB_OBJ.length).getDisplayValues()[0];
    if (String(atual[1]).trim() !== String(o.objetivo || '').trim()) throw new Error('A lista mudou; recarregue a página.');
    sh.getRange(l, 4).setValue(st);
    sh.getRange(l, 7).setValue(agora + ' · ' + (eu.nome || eu.email));
    if (obs) sh.getRange(l, 8).setValue(obs);
  } finally { lock.releaseLock(); }
  return { objetivos: objetivosLer_() };
}

/* ---------------- e-mail para a equipe pela Central (v15, 17/11/2026) ----------------
 * A pessoa escolhe destinatários da aba Equipe (por apelido), escreve e envia. O e-mail sai
 * da conta da TRX com o nome de quem escreveu, resposta (Reply-To) e cópia para ela.
 * Só vai para endereços da aba Equipe; cada envio fica registrado na aba Emails. */

const ABA_EMAILS = 'Emails';

function emailEnviar(cred, m) {
  const eu = exigir_(cred);
  m = m || {};
  const eq = equipeComPin_();
  const aps = (m.para || []).map(function (x) { return String(x).trim().toLowerCase(); });
  const dest = eq.filter(function (q) { return q.email && aps.indexOf(q.apelido) >= 0; })
    .map(function (q) { return q.email; })
    .filter(function (e, i, arr) { return arr.indexOf(e) === i; });
  if (!dest.length) throw new Error('Escolha pelo menos uma pessoa da equipe.');
  const assunto = String(m.assunto || '').trim().slice(0, 150);
  const corpo = String(m.corpo || '').trim();
  if (!assunto) throw new Error('Escreva o assunto.');
  if (!corpo) throw new Error('Escreva a mensagem.');
  if (corpo.length > 6000) throw new Error('Mensagem longa demais (máximo 6000 caracteres).');
  if (MailApp.getRemainingDailyQuota() < dest.length) throw new Error('A cota diária de e-mails da conta da TRX acabou. Tente amanhã.');
  const nome = eu.nome || eu.email;
  const opts = {
    to: dest.join(','),
    subject: '[TRX] ' + assunto,
    body: corpo + '\n\n--\n' + nome + ' · enviado pela Central TRX. Responda este e-mail para falar com ' + nome + '.',
    name: nome + ' · Central TRX'
  };
  if (eu.email) { opts.replyTo = eu.email; if (dest.indexOf(eu.email) < 0) opts.cc = eu.email; }
  MailApp.sendEmail(opts);
  try {
    const ss = planilha_();
    let sh = ss.getSheetByName(ABA_EMAILS);
    if (!sh) { sh = ss.insertSheet(ABA_EMAILS); sh.getRange(1, 1, 1, 4).setValues([['Quando', 'Autor', 'Para', 'Assunto']]); sh.setFrozenRows(1); }
    sh.appendRow([Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm'), nome, dest.join(', '), assunto]);
  } catch (e) {}
  return { enviados: dest.length };
}

/* ---------------- Producao dos socios: lancamento pela aba Relatorios da Central (17/11/2026) ----------------
 * A Carla sobe a planilha de apuracao na Central, a pagina agrupa os laudos no navegador e manda para ca
 * a producao do periodo. Aqui as linhas daquele periodo/contrato/modalidade sao substituidas na aba
 * Producao_Socios da Pipeline Licitacoes; as linhas de credito ADM e de outros contratos ficam como estao.
 * As colunas No_prazo e Horas_medianas ficam SEMPRE vazias: prazo nao e criterio entre socios.
 * Desde 17/11/2026 (v17): so lanca quem esta em producao_lancadores da Producao_Params, e o repasse
 * e a marca de socio sao calculados AQUI, pelas linhas repasse_padrao, "repasse: Nome" e socio_nomes
 * da mesma aba. A pagina manda so medico, exames e receita; nenhum valor de repasse mora no codigo. */

const ABA_PROD = 'Producao_Socios';
const PROD_COLS = ['Periodo', 'Medico', 'Socio', 'Contrato', 'Modalidade', 'Exames', 'No_prazo',
                   'Horas_medianas', 'Receita', 'Repasse', 'Fator', 'Obs'];

function producaoLancar(cred, d) {
  lancador_(cred);
  const regua = reguaProd_();
  d = d || {};
  const periodo = String(d.periodo || '').trim();
  const contrato = String(d.contrato || '').trim();
  const modalidade = String(d.modalidade || '').trim();
  const linhas = Array.isArray(d.linhas) ? d.linhas : [];
  if (!/^\d{4}-\d{2}$/.test(periodo)) throw new Error('Periodo invalido (use AAAA-MM).');
  if (!contrato || !modalidade) throw new Error('Diga o contrato e a modalidade.');
  if (!linhas.length) throw new Error('Nada para lancar.');
  if (linhas.length > 100) throw new Error('Lancamento grande demais.');
  // v18: modalidade que nao e RM so entra com a linha de repasse dela na Producao_Params
  repasseDe_('', regua, modalidade);

  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha esta ocupada. Tente de novo em alguns segundos.');
  try {
    const sh = SpreadsheetApp.openById(LICIT_ID).getSheetByName(ABA_PROD);
    if (!sh) throw new Error('A aba ' + ABA_PROD + ' nao existe na Pipeline Licitacoes.');
    const idx = cabecalho_(sh);
    PROD_COLS.forEach(function (c) { if (idx[c] === undefined) throw new Error('Falta a coluna ' + c + ' na aba ' + ABA_PROD + '.'); });

    // tira as linhas do mesmo periodo + contrato + modalidade, de baixo para cima
    const ult = sh.getLastRow();
    let tirou = 0;
    if (ult > 1) {
      const vals = sh.getRange(2, 1, ult - 1, sh.getLastColumn()).getDisplayValues();
      for (let i = vals.length - 1; i >= 0; i--) {
        const r = vals[i];
        if (String(r[idx['Periodo']]).trim() === periodo &&
            String(r[idx['Contrato']]).trim() === contrato &&
            String(r[idx['Modalidade']]).trim() === modalidade) { sh.deleteRow(i + 2); tirou++; }
      }
    }

    // escreve as novas na ordem das colunas da aba
    const larg = sh.getLastColumn();
    const novas = linhas.map(function (l) {
      const linha = new Array(larg).fill('');
      linha[idx['Periodo']] = periodo;
      linha[idx['Medico']] = String(l.medico || '').slice(0, 60);
      linha[idx['Socio']] = ehSocio_(l.medico, regua) ? 'sim' : 'nao';
      linha[idx['Contrato']] = contrato;
      linha[idx['Modalidade']] = modalidade;
      linha[idx['Exames']] = Number(l.exames) || 0;
      linha[idx['No_prazo']] = '';
      linha[idx['Horas_medianas']] = '';
      linha[idx['Receita']] = Number(l.receita) || 0;
      linha[idx['Repasse']] = Math.round((Number(l.exames) || 0) * repasseDe_(l.medico, regua, modalidade) * 100) / 100;
      linha[idx['Fator']] = 1;
      linha[idx['Obs']] = String(l.obs || '').slice(0, 220);
      return linha;
    });
    const inicio = sh.getLastRow() + 1;
    sh.getRange(inicio, 1, novas.length, larg).setValues(novas);
    return { tirou: tirou, gravou: novas.length, periodo: periodo, contrato: contrato };
  } finally { lock.releaseLock(); }
}

/* ---------------- regua de repasse e quem pode lancar (v17, 17/11/2026) ---------------- */

function semAcento_(t) {
  return String(t == null ? '' : t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
}

/** Le a Producao_Params: repasse padrao, repasse por medico, trechos de nome dos socios e lancadores. */
function reguaProd_() {
  const sh = SpreadsheetApp.openById(LICIT_ID).getSheetByName('Producao_Params');
  if (!sh) throw new Error('A aba Producao_Params nao existe na Pipeline Licitacoes.');
  const vals = sh.getRange(1, 1, sh.getLastRow(), 2).getDisplayValues();
  const r = { padrao: null, porMedico: {}, padraoMod: {}, porMedicoMod: {}, socios: [], lancadores: [] };
  const num = function (v) { const n = parseFloat(String(v).replace(/\./g, '').replace(',', '.')); return isNaN(n) ? null : n; };
  vals.forEach(function (l) {
    const k = String(l[0]).trim(), v = String(l[1]).trim(), kl = k.toLowerCase();
    const mMod = /^repasse_([a-z]{2,4}):(.*)$/.exec(kl);
    if (kl === 'repasse_padrao') r.padrao = num(v);
    // v18: repasse por modalidade. "repasse_padrao_TC" e o padrao da TC; "repasse_TC: Nome" e a excecao por medico
    else if (kl.indexOf('repasse_padrao_') === 0) { const n = num(v); if (n !== null) r.padraoMod[kl.slice(15).toUpperCase()] = n; }
    else if (mMod) { const n = num(v), md = mMod[1].toUpperCase(); if (n !== null) { r.porMedicoMod[md] = r.porMedicoMod[md] || {}; r.porMedicoMod[md][semAcento_(k.slice(k.indexOf(':') + 1))] = n; } }
    else if (kl.indexOf('repasse:') === 0) { const n = num(v); if (n !== null) r.porMedico[semAcento_(k.slice(8))] = n; }
    else if (kl === 'socio_nomes') r.socios = v.split(';').map(semAcento_).filter(String);
    else if (kl === 'producao_lancadores') r.lancadores = v.split(';').map(function (x) { return x.trim().toLowerCase(); }).filter(String);
  });
  if (r.padrao === null) throw new Error('Falta a linha repasse_padrao na Producao_Params.');
  return r;
}
/** Repasse por laudo. RM (ou modalidade vazia) usa repasse_padrao e "repasse: Nome", como sempre.
 *  Outra modalidade exige a linha repasse_padrao_<MOD> na Producao_Params: sem ela nada e lancado,
 *  para o repasse da RM nunca ser aplicado por engano a uma TC ou a um RX. */
function repasseDe_(nome, r, modalidade) {
  const k = semAcento_(nome);
  const md = String(modalidade || 'RM').trim().toUpperCase();
  if (md === 'RM' || md === 'MR') return r.porMedico[k] !== undefined ? r.porMedico[k] : r.padrao;
  if (r.padraoMod[md] === undefined) throw new Error('Falta a linha repasse_padrao_' + md + ' na Producao_Params. Sem ela a producao de ' + md + ' nao e lancada. Fale com o Marcos.');
  const pm = r.porMedicoMod[md] || {};
  return pm[k] !== undefined ? pm[k] : r.padraoMod[md];
}
function ehSocio_(nome, r) { const k = semAcento_(nome); return r.socios.some(function (x) { return k.indexOf(x) >= 0; }); }

/** Producao, entregas e medicao sao da area financeira: so entra quem esta em producao_lancadores. */
function lancador_(cred) {
  const eu = exigir_(cred);
  const ap = String(cred && cred.apelido || '').trim().toLowerCase();
  const lista = reguaProd_().lancadores;
  if (lista.indexOf(ap) < 0) throw new Error('Sem permissao: so ' + (lista.join(', ') || 'a area financeira') + ' lanca producao, entrega e medicao. Fale com o Marcos.');
  return eu;
}

/* ---------------- banco de entregas do HRVJ (v17, 17/11/2026) ----------------
 * Aba Entregas_HRVJ da Pipeline Licitacoes: Emissao | Total | Autor | Quando | Obs. Uma linha por
 * relatorio diario emitido; o relatorio seguinte compara com a ultima linha anterior a data dele.
 * Guardar a mesma data de novo substitui o total. A cada entrega a linha automatica do
 * Destaque_ISGH (titulo que comeca por "Producao do HRVJ") e reescrita com o total e o saldo. */

const ABA_ENT = 'Entregas_HRVJ';
const ABA_DESTAQUE = 'Destaque_ISGH';
const DESTAQUE_AUTO = 'Produção do HRVJ';

function dataBr_(t) { const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(String(t || '').trim()); return m ? m[3] + m[2] + m[1] : ''; }

/* v18 (20/11/2026): cada hospital e cada modalidade tem o seu banco de entregas. A RM do HRVJ
 * continua na aba Entregas_HRVJ, como estava. O resto mora na aba Entregas_Geral
 * (Contrato | Modalidade | Emissao | Total | Autor | Quando | Obs), criada na primeira gravacao.
 * A linha automatica do Destaque_ISGH da RM do HRVJ comeca por "Producao do HRVJ"; as outras
 * comecam por "Producao <SIGLA> <MOD>:", para uma nunca casar com a outra. */
const ABA_ENT_GERAL = 'Entregas_Geral';
const ENT_GERAL_COLS = ['Contrato', 'Modalidade', 'Emissao', 'Total', 'Autor', 'Quando', 'Obs'];

function entregaGuardar(cred, e) {
  const eu = lancador_(cred);
  e = e || {};
  const emissao = String(e.emissao || '').trim();
  const total = parseInt(e.total, 10);
  const pacote = parseInt(e.pacote, 10) || 0;
  const contrato = String(e.contrato || 'HRVJ').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 12);
  let modalidade = String(e.modalidade || 'RM').toUpperCase().replace(/[^A-Z]/g, '').slice(0, 4);
  if (modalidade === 'MR') modalidade = 'RM';
  if (!dataBr_(emissao)) throw new Error('Data de emissao invalida (use DD/MM/AAAA).');
  if (!(total > 0) || total > 100000) throw new Error('Total invalido.');
  if (!contrato || !modalidade) throw new Error('Diga o hospital e a modalidade da entrega.');
  const legado = contrato === 'HRVJ' && modalidade === 'RM';
  const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
  const autor = eu.nome || eu.email;
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha esta ocupada. Tente de novo em alguns segundos.');
  try {
    const ss = SpreadsheetApp.openById(LICIT_ID);
    let todas = [];
    if (legado) {
      const sh = ss.getSheetByName(ABA_ENT);
      if (!sh) throw new Error('A aba ' + ABA_ENT + ' nao existe na Pipeline Licitacoes.');
      const ult = sh.getLastRow();
      const vals = ult > 1 ? sh.getRange(2, 1, ult - 1, 2).getDisplayValues() : [];
      let linha = 0;
      vals.forEach(function (r, i) { if (String(r[0]).trim() === emissao) linha = i + 2; });
      const nova = [emissao, total, autor, agora, String(e.obs || '').slice(0, 200)];
      if (linha) sh.getRange(linha, 1, 1, 5).setValues([nova]); else sh.appendRow(nova);
      SpreadsheetApp.flush();
      todas = sh.getRange(2, 1, sh.getLastRow() - 1, 2).getDisplayValues()
        .map(function (r) { return [String(r[0]).trim(), parseInt(r[1], 10) || 0]; });
    } else {
      let sh = ss.getSheetByName(ABA_ENT_GERAL);
      if (!sh) { sh = ss.insertSheet(ABA_ENT_GERAL); sh.getRange(1, 1, 1, ENT_GERAL_COLS.length).setValues([ENT_GERAL_COLS]); sh.setFrozenRows(1); }
      const ult = sh.getLastRow();
      const vals = ult > 1 ? sh.getRange(2, 1, ult - 1, 3).getDisplayValues() : [];
      let linha = 0;
      vals.forEach(function (r, i) {
        if (String(r[0]).trim().toUpperCase() === contrato && String(r[1]).trim().toUpperCase() === modalidade && String(r[2]).trim() === emissao) linha = i + 2;
      });
      const nova = [contrato, modalidade, emissao, total, autor, agora, String(e.obs || '').slice(0, 200)];
      if (linha) sh.getRange(linha, 1, 1, 7).setValues([nova]); else sh.appendRow(nova);
      SpreadsheetApp.flush();
      todas = sh.getRange(2, 1, sh.getLastRow() - 1, 4).getDisplayValues()
        .filter(function (r) { return String(r[0]).trim().toUpperCase() === contrato && String(r[1]).trim().toUpperCase() === modalidade; })
        .map(function (r) { return [String(r[2]).trim(), parseInt(r[3], 10) || 0]; });
    }
    todas = todas.filter(function (r) { return dataBr_(r[0]) && r[1] > 0; })
      .sort(function (a, b) { return dataBr_(a[0]) < dataBr_(b[0]) ? -1 : 1; });
    // linha automatica do Destaque_ISGH: so quando a entrega guardada e a mais recente
    try {
      const ultima = todas[todas.length - 1];
      if (ultima && ultima[0] === emissao) {
        const ant = todas.length > 1 ? todas[todas.length - 2] : null;
        const prefixo = legado ? DESTAQUE_AUTO : ('Produção ' + contrato + ' ' + modalidade);
        const titulo = prefixo + ': ' + total + ' laudos até ' + emissao.slice(0, 5);
        const texto = 'Atualizado sozinho pela aba Relatórios em ' + agora + '. Entrega de ' + emissao + ' com ' + total + ' laudos acumulados'
          + (legado ? '' : ' de ' + modalidade + ' do ' + contrato)
          + (ant ? ', ' + (total - ant[1]) + ' liberados desde a entrega de ' + ant[0] : '') + '.'
          + (pacote ? ' Saldo do pacote de ' + pacote + ': ' + Math.max(0, pacote - total) + ' laudos.' : '');
        const sd = ss.getSheetByName(ABA_DESTAQUE);
        if (sd) {
          const dv = sd.getRange(1, 1, sd.getLastRow(), 2).getDisplayValues();
          let ld = 0;
          dv.forEach(function (r, i) { if (i && String(r[1]).indexOf(legado ? DESTAQUE_AUTO : prefixo + ':') === 0) ld = i + 1; });
          if (ld) sd.getRange(ld, 2, 1, 2).setValues([[titulo, texto]]);
          else sd.appendRow(['contrato', titulo, texto, '', 'Carla', 0, '']);
        }
      }
    } catch (err) {}
    return { entregas: todas, quando: agora, contrato: contrato, modalidade: modalidade };
  } finally { lock.releaseLock(); }
}

/* ---------------- medicao na planilha de cobranca (v17, 17/11/2026) ----------------
 * O fechamento para nota fiscal da aba Relatorios grava na aba Medicoes da planilha
 * "Faturamento e Cobranca HRVJ ISGH" os laudos de RM (F) e a data do relatorio (K) da medicao
 * escolhida, para a tarefa de cobranca enxergar sem ninguem digitar de novo. So F e K: Q, R e S
 * sao formulas e o resto e preenchimento da equipe. */

const FATUR_ID = '14i23-uo6aCZ30SM-XoSKtrqIN4dyCmcsGyFZ1RdFCTk';

function medicaoGravar(cred, m) {
  const eu = lancador_(cred);
  m = m || {};
  const numero = String(m.numero || '').trim().toUpperCase();
  const laudos = parseInt(m.laudos, 10);
  const enviado = String(m.enviadoEm || '').trim();
  if (!/^[AB]-\d$/.test(numero)) throw new Error('Medicao invalida (use A-1, A-2, B-1...).');
  if (!(laudos > 0) || laudos > 100000) throw new Error('Quantidade de laudos invalida.');
  if (enviado && !dataBr_(enviado)) throw new Error('Data do relatorio invalida (use DD/MM/AAAA).');
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) throw new Error('A planilha esta ocupada. Tente de novo em alguns segundos.');
  try {
    const sh = SpreadsheetApp.openById(FATUR_ID).getSheetByName('Medicoes');
    if (!sh) throw new Error('A aba Medicoes nao existe na planilha de cobranca.');
    const col = sh.getRange(1, 1, Math.min(sh.getLastRow(), 40), 1).getDisplayValues();
    let linha = 0;
    col.forEach(function (r, i) { if (String(r[0]).trim().toUpperCase() === numero) linha = i + 1; });
    if (!linha) throw new Error('Nao achei a medicao ' + numero + ' na aba Medicoes.');
    const antes = sh.getRange(linha, 6).getDisplayValue();
    sh.getRange(linha, 6).setValue(laudos);
    if (enviado) sh.getRange(linha, 11).setValue(enviado);
    const agora = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy HH:mm');
    const obs = sh.getRange(linha, 20);
    obs.setValue((String(obs.getValue() || '') + ' | ' + agora + ': ' + (eu.nome || eu.email) + ' gravou ' + laudos + ' laudos de RM pela aba Relatórios'
      + (antes && String(antes) !== String(laudos) ? ' (antes: ' + antes + ')' : '') + (enviado ? ', relatório de ' + enviado : '') + '.').replace(/^ \| /, ''));
    return { numero: numero, laudos: laudos, antes: antes };
  } finally { lock.releaseLock(); }
}
