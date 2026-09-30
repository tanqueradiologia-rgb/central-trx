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
 * Cada frente (clínicas hoje; licitações e quadro depois) é uma entrada em FRENTES.
 */

const FRENTES = {
  clinicas: {
    titulo: 'Clínicas particulares',
    aba: 'Pipeline',
    chave: 'Clinica',            // coluna que identifica a linha
    chave2: 'Cidade',            // desempate quando há nomes repetidos
    // colunas mostradas na lista e no detalhe (só leitura)
    leitura: ['Clinica', 'Cidade', 'UF', 'Prioridade', 'Modalidades', 'Gancho', 'Responsavel', 'Fase',
      'Decisor', 'Cargo', 'Toque_atual', 'Inicio_cadencia', 'Proximo_toque', 'Ultima_atualizacao',
      'Resultado', 'Notas', 'Proxima_Acao', 'Score', 'Faixa', 'Dor', 'Cobertura', 'Janela',
      'Sinal_de_compra', 'Necessidade', 'Sinal_operacional', 'Nota_RA', 'O_que_reclamam', 'Medido_em'],
    // colunas que a equipe pode mudar pelo app
    edicao: {
      Fase: { tipo: 'lista', opcoes: ['Mapeando', 'Pesquisando decisor', 'Em cadencia', 'Decisor engajado',
        'Handoff gestora', 'Diagnostico operacional', 'Fechado', 'Sem retorno', 'Descartado'] },
      Responsavel: { tipo: 'equipe' },
      Proxima_Acao: { tipo: 'texto' },
      Proximo_toque: { tipo: 'data' },
      Toque_atual: { tipo: 'texto' },
      Resultado: { tipo: 'texto' },
      Decisor: { tipo: 'texto' },
      Cargo: { tipo: 'texto' }
    },
    carimbo: 'Ultima_atualizacao'   // gravado com a data de hoje a cada edição
  }
};

const PLANILHA_ID = '1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0';  // Pipeline TRX — Prospecção (fonte da verdade)
const ABA_HIST = 'Historico';
const ABA_EQUIPE = 'Equipe';
const TZ = 'America/Sao_Paulo';

function doGet() {
  return HtmlService.createTemplateFromFile('Index').evaluate()
    .setTitle('Central TRX · Edição')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/* ---------------- leitura ---------------- */

function planilha_() { return SpreadsheetApp.openById(PLANILHA_ID); }

function cabecalho_(sh) {
  const h = sh.getRange(1, 1, 1, sh.getLastColumn()).getDisplayValues()[0];
  const idx = {};
  h.forEach(function (n, i) { if (n) idx[String(n).trim()] = i; });
  return idx;
}

function equipe_() {
  const sh = planilha_().getSheetByName(ABA_EQUIPE);
  if (!sh || sh.getLastRow() < 2) return [];
  return sh.getRange(2, 1, sh.getLastRow() - 1, 4).getDisplayValues()
    .filter(function (r) { return r[0] && String(r[3]).toLowerCase() !== 'não' && String(r[3]).toLowerCase() !== 'nao'; })
    .map(function (r) { return { nome: r[0], email: r[1], apelido: (r[2] || r[0]).toLowerCase() }; });
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
  const sh = planilha_().getSheetByName(cfg.aba);
  const idx = cabecalho_(sh);
  const n = sh.getLastRow() - 1;
  const vals = n > 0 ? sh.getRange(2, 1, n, sh.getLastColumn()).getDisplayValues() : [];
  const cols = cfg.leitura.filter(function (c) { return idx[c] !== undefined; });
  const linhas = [];
  vals.forEach(function (r, i) {
    if (!String(r[idx[cfg.chave]] || '').trim()) return;
    const o = { _l: i + 2, _k: r[idx[cfg.chave]] + (cfg.chave2 ? ' · ' + r[idx[cfg.chave2]] : '') };
    cols.forEach(function (c) { o[c] = r[idx[c]]; });
    linhas.push(o);
  });
  const hist = historico_(frente);
  return {
    frente: frente,
    titulo: cfg.titulo,
    usuario: Session.getActiveUser().getEmail() || '',
    agora: Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd'T'HH:mm"),
    edicao: cfg.edicao,
    equipe: equipe_(),
    linhas: linhas,
    historico: hist,
    planilha: planilha_().getUrl(),
    gid: sh.getSheetId()
  };
}

/* ---------------- gravação ---------------- */

/**
 * pedido = { frente, linha, chave, chave2, campos: {Coluna: valor}, nota, mencoes: [email] }
 * Confere se a linha ainda é a mesma clínica antes de gravar.
 */
function salvar(pedido) {
  const cfg = FRENTES[pedido.frente || 'clinicas'];
  if (!cfg) throw new Error('Frente desconhecida.');
  const lock = LockService.getScriptLock();   // projeto separado: getDocumentLock() devolve null fora da planilha
  if (!lock.tryLock(20000)) throw new Error('A planilha está ocupada. Tente de novo em alguns segundos.');
  try {
    const ss = planilha_();
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
      const novo = String(pedido.campos[c] == null ? '' : pedido.campos[c]).trim();
      const velho = String(atual[idx[c]] || '').trim();
      if (novo === velho) return;
      if (cfg.edicao[c].tipo === 'lista' && novo && cfg.edicao[c].opcoes.indexOf(novo) < 0)
        throw new Error('Valor inválido para ' + c + ': ' + novo);
      sh.getRange(linha, idx[c] + 1).setValue(novo);
      hist.push([agora, autor, linha, nome, pedido.frente + ':mudança', c, velho, novo, '', '']);
      mudou = true;
    });

    const nota = String(pedido.nota || '').trim();
    const menc = (pedido.mencoes || []).filter(String);
    if (nota) {
      hist.push([agora, autor, linha, nome, pedido.frente + ':nota', '', '', '', nota, menc.join(', ')]);
      mudou = true;
    }
    if (!mudou) return { ok: true, nada: true };

    if (cfg.carimbo && idx[cfg.carimbo] !== undefined)
      sh.getRange(linha, idx[cfg.carimbo] + 1).setValue(Utilities.formatDate(new Date(), TZ, 'yyyy-MM-dd'));

    const hs = ss.getSheetByName(ABA_HIST);
    hs.getRange(hs.getLastRow() + 1, 1, hist.length, 10).setValues(hist);
    SpreadsheetApp.flush();

    if (nota && menc.length) avisar_(menc, autor, nome, nota, linha, cfg);
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

function avisar_(emails, autor, nome, nota, linha, cfg) {
  const url = ScriptApp.getService().getUrl();
  emails.forEach(function (e) {
    try {
      MailApp.sendEmail({
        to: e,
        subject: 'Central TRX: nota em ' + nome,
        htmlBody: '<p><b>' + autor + '</b> marcou você numa nota sobre <b>' + nome + '</b>:</p>' +
          '<blockquote>' + nota.replace(/</g, '&lt;') + '</blockquote>' +
          '<p><a href="' + url + '">Abrir a Central TRX · Edição</a> (linha ' + linha + ' da aba ' + cfg.aba + ').</p>'
      });
    } catch (err) { console.warn('Aviso não enviado para ' + e + ': ' + err); }
  });
}
