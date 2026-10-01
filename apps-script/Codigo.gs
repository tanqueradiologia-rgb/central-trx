/**
 * Central TRX · Edição
 * App web (projeto próprio, separado dos scripts da planilha) que lê e grava na
 * "Pipeline TRX — Prospecção (fonte da verdade)" pelo ID em PLANILHA_ID.
 *
 * A planilha continua sendo a fonte da verdade. O app só lê e grava nela,
 * sempre com o login Google de quem está usando (implantar como
 * "Executar como: usuário que acessa o app"). Quem não tem acesso de edição
 * à planilha não consegue gravar.
 *
 * Cada frente é uma entrada em FRENTES: clínicas (Pipeline TRX), licitações e quadro de
 * credenciamento (Pipeline Licitações TRX, aba Licitacoes, separadas pela coluna Trilha).
 * Historico e Equipe ficam sempre na Pipeline TRX, para todas as frentes.
 */

const PLANILHA_ID = '1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0';  // Pipeline TRX — Prospecção (fonte da verdade): clínicas, Historico e Equipe
const LICIT_ID = '1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8';    // Pipeline Licitações TRX (fonte da verdade)

// ROTEIRO-INICIO (gerado por scripts/gerar_roteiro.py a partir de config/roteiro.json: não edite aqui)
const ROTEIRO = {"_sobre":"Fonte única do roteiro comercial da TRX. scripts/gerar_roteiro.py gera site/roteiro.js (Central) e o bloco ROTEIRO do apps-script/Codigo.gs (app de Edição). O roteiro orienta; quem decide é a equipe.","versao":"01/10/2026 · roteiro rev. 26/08/2026 + homologação e implantação","papeis":{"Carla":"Prospecção: pescaria do decisor, cadência de toques, licitações e quadro público.","Gestor":"Gestor do contrato. É papel do contrato, não cargo fixo: cada cliente tem o seu.","Socios medicos":"Dois sócios médicos na conversa clínica: um traz o dado, o outro guarda o preço.","Marcos":"Monta a proposta com o gestor, decide participação em licitação e assina com o certificado A1.","Bruno Sato":"Sócio médico responsável pelo fechamento: negociação final e assinatura, com liberdade de canal, ritmo e formato.","TI":"Homologação e implantação: integração com o PACS e os sistemas do cliente."},"regras":["Preço só na etapa 4. Quando o número sai antes, a conversa vira comparação de tabela e a TRX perde onde é mais forte, porque a diferença dela é clínica.","A etapa vira com a entrega, não com a impressão. Sem a entrega, o dono anterior continua responsável.","Toda proposta sai com a TRX em cópia, para o grupo acompanhar a negociação sem precisar perguntar.","Os sócios nunca discordam na frente do cliente sobre o valor do serviço."],"particulares":{"titulo":"Clínicas e hospitais particulares","etapas":[{"n":1,"nome":"Pescaria do decisor","dono":"Carla","preco":false,"objetivo":"Encontrar e engajar quem decide de verdade: o radiologista ou o responsável técnico, não só o administrador. A cadência de toques acontece toda aqui.","fecha":"O convite da reunião chega às mãos do gestor do contrato. Até o convite passar, o lead é da Carla."},{"n":2,"nome":"Reunião de diagnóstico","dono":"Gestor","preco":false,"objetivo":"Ouvir a operação do cliente e mapear onde dói: tempo de laudo, plantão descoberto, PACS, fila parada. Sair da reunião com a conversa clínica marcada, com quem decide e, de preferência, com o radiologista.","fecha":"O gestor entrega aos sócios médicos a ata da reunião, com a lista de participantes."},{"n":3,"nome":"Conversa clínica","dono":"Socios medicos","preco":false,"objetivo":"Médico falando com médico sobre o problema clínico. Combinem antes quem faz o quê: um traz o dado (tempo de laudo medido, risco, SLA, LGPD) e o outro guarda o preço. O guardião não diz número.","fecha":"O cliente diz que quer o serviço, ainda sem nenhum número na mesa."},{"n":4,"nome":"Proposta escrita","dono":"Marcos","preco":true,"objetivo":"O preço entra, por escrito. Marcos e gestor montam a proposta, o Marcos manda ao gestor e o gestor encaminha ao cliente.","fecha":"O e-mail com a proposta é enviado ao cliente, com a TRX em cópia."},{"n":5,"nome":"Fechamento","dono":"Bruno Sato","preco":true,"objetivo":"Negociação final e assinatura. O responsável pelo fechamento tem liberdade total de canal, ritmo e formato.","fecha":"O contrato é assinado."},{"n":6,"nome":"Homologação e implantação","dono":"Gestor","preco":true,"objetivo":"Integração com o PACS e os sistemas do cliente, acessos, VPN, testes de laudo e homologação pelo cliente, como no HNSA. O gestor do contrato conduz com a TI.","fecha":"O cliente homologa e o primeiro laudo sai em produção."}],"fases":{"Mapeando":{"e":1,"resp":"Carla","faz":"Conferir se a clínica tem perfil (modalidades, gancho e a Dor medida). Se tiver, passar para Pesquisando decisor."},"Pesquisando decisor":{"e":1,"resp":"Carla","faz":"Achar o radiologista ou o responsável técnico e quem assina contratos (quadro de sócios no CNPJ, site, Instagram, LinkedIn). Preencher Decisor e Cargo e marcar o Início da cadência."},"Em cadencia":{"e":1,"resp":"Carla","faz":"Rodar os 6 toques em cerca de 21 dias, alternando e-mail, telefone e WhatsApp. A cada contato, atualizar Toque atual e Próximo toque. Nenhum número de preço."},"Decisor engajado":{"e":1,"resp":"Carla","faz":"O decisor topou conversar. Marcar a reunião de diagnóstico e entregar o convite ao gestor do contrato; aí a Fase vira Handoff gestor."},"Handoff gestor":{"e":2,"resp":"Gestor","faz":"Convite nas mãos do gestor. Ele confirma a reunião e lê o histórico da linha (decisor, gancho, notas)."},"Diagnostico operacional":{"e":2,"resp":"Gestor","faz":"Reunião de diagnóstico: tempo de laudo, plantão descoberto, PACS, fila parada. Sair com a conversa clínica marcada e entregar a ata, com participantes, aos sócios médicos."},"Conversa clinica":{"e":3,"resp":"Socios medicos","faz":"Combinar antes quem traz o dado e quem guarda o preço. Ninguém diz número. Termina quando o cliente diz que quer o serviço."},"Proposta escrita":{"e":4,"resp":"Marcos","faz":"Marcos e gestor montam a proposta; o Marcos manda ao gestor e o gestor envia ao cliente, com a TRX em cópia."},"Negociacao":{"e":5,"resp":"Bruno Sato","faz":"Negociação final e assinatura conduzidas pelo Bruno Sato."},"Fechado":{"e":6,"resp":"Gestor","faz":"Contrato assinado. Abrir a homologação e implantação com a TI e registrar o combinado em Resultado."},"Implantacao":{"e":6,"resp":"Gestor","faz":"Integração com o PACS, acessos, testes de laudo e homologação pelo cliente."},"Em operacao":{"e":7,"resp":"Gestor","faz":"Contrato em produção. A gestão do contrato, o faturamento e a distribuição de valores entram numa fase futura da Central."},"Sem retorno":{"e":0,"resp":"Carla","faz":"A cadência terminou sem resposta. Pode voltar à etapa 1 se surgir sinal novo (vaga de radiologista, troca de dono, unidade nova)."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}},"cadencia":[{"n":1,"dia":0,"canal":"E-mail","obj":"Abertura: apresentar a TRX e o gancho específico da clínica."},{"n":2,"dia":2,"canal":"Telefone","obj":"Falar com o decisor ou descobrir quem responde por contratos."},{"n":3,"dia":5,"canal":"WhatsApp","obj":"Mensagem curta de valor, retomando o e-mail."},{"n":4,"dia":9,"canal":"Telefone","obj":"Nova tentativa, em horário ou turno diferente."},{"n":5,"dia":14,"canal":"WhatsApp","obj":"Benefícios concretos e convite para 15 minutos de conversa."},{"n":6,"dia":21,"canal":"E-mail","obj":"Encerramento educado, deixando a porta aberta."}]},"licitacoes":{"titulo":"Licitações, credenciamentos e pregões","aviso":"No público o caminho é o edital: não há cadência nem conversa de preço antes da disputa. Mapa proposto pelo Claude a partir do que já funciona; ajuste com o Marcos.","etapas":[{"n":1,"nome":"Triagem","dono":"Carla","preco":false,"objetivo":"Ler o resumo, conferir no mesmo dia o cadastro na plataforma da disputa (a TRX já perdeu processos por cadastro) e anotar travas: CNES, presencial, atestado, exclusividade ME/EPP.","fecha":"O Marcos decide participar, ou a linha vai para Descartado com o motivo em Resultado."},{"n":2,"nome":"Edital e habilitação","dono":"Carla","preco":false,"objetivo":"Fase Montando habilitacao: a pasta do processo e o checklist saem sozinhos. A Carla adapta as declarações e o Marcos assina com o certificado A1.","fecha":"Documentos e proposta enviados na plataforma dentro do prazo."},{"n":3,"nome":"Disputa e julgamento","dono":"Marcos","preco":true,"objetivo":"A Carla acompanha a sessão e as diligências. O Marcos define o lance, nunca abaixo do piso, e responde recursos.","fecha":"Resultado publicado: habilitado, credenciado, ganho ou perdido."},{"n":4,"nome":"Contrato","dono":"Marcos","preco":true,"objetivo":"Assinar o contrato ou o termo de credenciamento e definir o gestor do contrato.","fecha":"Contrato ou termo assinado e gestor definido."},{"n":5,"nome":"Homologação e implantação","dono":"Gestor","preco":true,"objetivo":"Integração com o PACS e os sistemas do órgão, acessos, testes de laudo e homologação, como no HNSA.","fecha":"Primeiro laudo em produção."}],"fases":{"Mapeado":{"e":1,"resp":"Carla","faz":"Ler o resumo, conferir o cadastro na plataforma hoje e levar ao Marcos a decisão de participar."},"Lendo edital":{"e":1,"resp":"Carla","faz":"Levantar exigências e travas (CNES, presencial, atestado, índices, ME/EPP, preço por laudo contra o piso) e registrar em Trava."},"Montando habilitacao":{"e":2,"resp":"Carla","faz":"A pasta e o checklist saem sozinhos. Adaptar as declarações e separar o que o Marcos assina com o A1."},"Documentos enviados":{"e":3,"resp":"Carla","faz":"Acompanhar a plataforma e responder diligências no prazo."},"Proposta enviada":{"e":3,"resp":"Carla","faz":"Acompanhar a sessão. Lance só com o Marcos e nunca abaixo do piso."},"Em analise":{"e":3,"resp":"Carla","faz":"Acompanhar a análise e responder diligências."},"Em julgamento":{"e":3,"resp":"Marcos","faz":"Acompanhar o julgamento e decidir sobre recurso."},"Habilitado":{"e":4,"resp":"Marcos","faz":"Aguardar a homologação e preparar a assinatura."},"Credenciado":{"e":4,"resp":"Marcos","faz":"Assinar o termo e definir o gestor do contrato."},"Ganho":{"e":4,"resp":"Marcos","faz":"Assinar o contrato e definir o gestor do contrato."},"Implantacao":{"e":5,"resp":"Gestor","faz":"Integração com o PACS, acessos, testes de laudo e homologação pelo órgão."},"Em operacao":{"e":6,"resp":"Gestor","faz":"Contrato em produção. Gestão, faturamento e distribuição de valores entram numa fase futura."},"Perdido":{"e":0,"resp":"Carla","faz":"Registrar em Resultado por que perdemos (preço, documentação, cadastro, prazo)."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}}},"quadro":{"titulo":"Quadro público (municípios sem processo aberto)","aviso":"Prospecção ativa no público: o objetivo é fazer o órgão abrir credenciamento. Quando abrir, a linha vira processo na aba Licitações.","etapas":[{"n":1,"nome":"Contato com o órgão","dono":"Carla","preco":false,"objetivo":"Achar o secretário de saúde, o diretor da unidade ou o consórcio (CIS) e enviar a apresentação com o pacote de habilitação.","fecha":"O órgão responde."},{"n":2,"nome":"Reunião com o órgão","dono":"Gestor","preco":false,"objetivo":"Apresentar a TRX e entender volume, equipamentos e a forma de contratar (credenciamento, dispensa, adesão a ata).","fecha":"O órgão abre o processo; a linha passa para Licitações."}],"fases":{"Em aberto":{"e":1,"resp":"Carla","faz":"Achar o contato certo e enviar a apresentação."},"E-mail enviado":{"e":1,"resp":"Carla","faz":"Retomar em cerca de 7 dias por telefone ou WhatsApp."},"Documentos enviados":{"e":1,"resp":"Carla","faz":"Confirmar o recebimento e perguntar se pretendem abrir credenciamento."},"Respondeu":{"e":2,"resp":"Carla","faz":"Marcar a reunião e entregar o convite ao gestor."},"Reuniao marcada":{"e":2,"resp":"Gestor","faz":"Reunião com o órgão: volume, equipamentos e forma de contratação."},"Sem interesse":{"e":0,"resp":"","faz":"Registrar o motivo em Resultado."},"Descartado":{"e":0,"resp":"","faz":"Fora do funil. O motivo fica em Resultado."}}}};
// ROTEIRO-FIM

// Fases e responsáveis seguem o roteiro comercial (config/roteiro.json). A validação da planilha usa as mesmas listas.
const FASES_CLINICA = Object.keys(ROTEIRO.particulares.fases);
const RESP_CLINICA = ['Carla', 'Gestor', 'Socios medicos', 'Marcos', 'Bruno Sato', 'TI'];
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

function doGet(e) {
  // Link vindo da Central (GitHub): ?f=clinicas|licitacoes|quadro&l=<linha da planilha> abre a linha direto.
  const t = HtmlService.createTemplateFromFile('Index');
  const p = (e && e.parameter) || {};
  t.abrirFrente = /^(clinicas|licitacoes|quadro)$/.test(p.f || '') ? p.f : '';
  t.abrirLinha = /^\d{1,6}$/.test(p.l || '') ? p.l : '';
  return t.evaluate()
    .setTitle('Central TRX · Edição')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/* ---------------- leitura ---------------- */

function planilha_(id) { return SpreadsheetApp.openById(id || PLANILHA_ID); }

function cabecalho_(sh) {
  const h = sh.getRange(1, 1, 1, sh.getLastColumn()).getDisplayValues()[0];
  const idx = {};
  h.forEach(function (n, i) { if (n) idx[String(n).trim()] = i; });
  return idx;
}

/** Aba Equipe: Nome | Email | Apelido | Ativo | Papel (papéis do roteiro separados por vírgula). */
function equipe_() {
  const sh = planilha_().getSheetByName(ABA_EQUIPE);
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, 5).getDisplayValues()
    .filter(function (r) { return r[0] && String(r[3]).toLowerCase() !== 'não' && String(r[3]).toLowerCase() !== 'nao'; })
    .map(function (r) {
      return { nome: r[0], email: String(r[1] || '').trim(), apelido: (r[2] || r[0]).toLowerCase(),
        papeis: String(r[4] || '').split(',').map(function (x) { return x.trim(); }).filter(String) };
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

/** Menções e passagens dos últimos 30 dias para quem está usando o app. */
function getAvisos() {
  const eu = String(Session.getActiveUser().getEmail() || '').toLowerCase();
  const sh = planilha_().getSheetByName(ABA_HIST);
  const lidoAte = Number(PropertiesService.getUserProperties().getProperty('lidoAte') || 0);
  if (!eu || !sh || sh.getLastRow() < 2) return { avisos: [], novos: 0 };
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
      tipo: tipo.replace(/^[^:]+:/, ''), msg: r[8], novo: t > lidoAte });
  });
  out.sort(function (a, b) { return b.t - a.t; });
  return { avisos: out.slice(0, 60), novos: out.filter(function (a) { return a.novo; }).length };
}

function marcarLidos() { PropertiesService.getUserProperties().setProperty('lidoAte', String(Date.now())); return true; }

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

/** Tudo o que a página precisa para abrir. */
function getDados(frente) {
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
    usuario: Session.getActiveUser().getEmail() || '',
    avisos: getAvisos(),
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
    const autor = Session.getActiveUser().getEmail() || 'desconhecido';
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
