#!/usr/bin/env python3
"""Medição do fluxo (Kanban) da Central TRX, 27/11/2026.

O que faz, a cada rodada:
  1. lê as linhas das frentes (clínicas, licitações, quadro público e documentos) nos arquivos
     que a rodada já baixou;
  2. compara a Fase de cada linha com a da rodada anterior (aba Fluxo_Estado) e registra cada
     passagem na aba Fluxo_Transicoes. A hora exata vem da aba Historico quando a mudança foi
     feita pelo app de Edição; mudança feita direto na planilha entra com a hora da rodada.
     Assim a medição não depende de a equipe usar sempre o app;
  3. guarda uma foto por dia da contagem por fase (aba Fluxo_Fotos);
  4. calcula vazão por semana, tempo por etapa (percentis 50, 70 e 85), teto provisório por
     frente e a previsão por simulação, e escreve tudo em fluxo.json para o build_central.py.

As três abas ficam na planilha Pipeline Licitações TRX, onde a conta de serviço já é editora.
Sem GOOGLE_SA_JSON (teste local) o estado fica em arquivos .json na pasta indicada.
Falha aqui nunca derruba a página: o build segue sem o bloco de fluxo.

Uso: python scripts/fluxo.py [--local PASTA]
"""
import argparse, datetime as dt, json, os, random, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = dt.timezone(dt.timedelta(hours=-3))
LICIT_SHEET = "1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8"
ABA_ESTADO, ABA_TRANS, ABA_FOTOS = "Fluxo_Estado", "Fluxo_Transicoes", "Fluxo_Fotos"
CAB = {ABA_ESTADO: ["Frente", "Chave", "Fase", "Desde", "Fonte", "Desde_etapa"],
       ABA_TRANS: ["Quando", "Frente", "Chave", "De", "Para", "Fonte"],
       ABA_FOTOS: ["Dia", "Frente", "Fase", "Itens"]}
FRENTES = ("clinicas", "licitacoes", "quadro", "documentos")
ROT = {"clinicas": "particulares", "licitacoes": "licitacoes", "quadro": "quadro"}
DOC_FASES = {"Em dia": 0, "A vencer": 1, "Vencido": 2}
WIP = "(em andamento)"          # linha especial da foto: total em andamento da frente


# ---------------------------------------------------------------- leitura das frentes

def _tabela(path):
    try:
        v = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    rows = v.get("values") if isinstance(v, dict) else v
    if not rows or len(rows) < 2:
        return []
    H = [str(h).strip() for h in rows[0]]
    return [dict(zip(H, list(r) + [""] * (len(H) - len(r)))) for r in rows[1:]]


def _iso(v):
    """dd/mm/aaaa [hh:mm] ou aaaa-mm-dd[ hh:mm] -> 'aaaa-mm-ddThh:mm' (ou só a data)."""
    s = str(v or "").strip()
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if m:
        d, mo, y, h, mi = m.groups()
        return f"{y}-{mo}-{d}" + (f"T{int(h):02d}:{mi}" if h else "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?", s)
    if m:
        y, mo, d, h, mi = m.groups()
        return f"{y}-{mo}-{d}" + (f"T{h}:{mi}" if h else "")
    return ""


def _dt(iso):
    try:
        return dt.datetime.fromisoformat(iso if len(iso) > 10 else iso + "T12:00")
    except Exception:
        return None


def fase_documento(d):
    st = str(d.get("Status") or "").strip().upper()
    if st == "VENCIDO" or str(d.get("Desatualizado (motivo)") or "").strip():
        return "Vencido"
    if st.startswith("VENCE EM"):
        return "A vencer"
    return "Em dia"


def linhas_das_frentes(pasta="."):
    """{frente: {chave: {"fase":..., "carimbo": iso}}} a partir dos json que a rodada baixou."""
    p = lambda n: os.path.join(pasta, n)
    out = {f: {} for f in FRENTES}
    for d in _tabela(p("pipeline.json")):
        nome = str(d.get("Clinica") or "").strip()
        if not nome:
            continue
        chave = nome + " · " + str(d.get("Cidade") or "").strip()      # igual ao Historico do app
        out["clinicas"][chave] = {"fase": str(d.get("Fase") or "").strip() or "Sem fase",
                                  "carimbo": _iso(d.get("Ultima_atualizacao"))}
    for d in _tabela(p("licitacoes.json")):
        rid, t = str(d.get("ID") or "").strip(), str(d.get("Trilha") or "").strip()
        if not rid:
            continue
        if t in ("CREDENCIAMENTO", "PREGAO"):
            out["licitacoes"][rid] = {"fase": str(d.get("Fase") or "").strip() or "Mapeado",
                                      "carimbo": _iso(d.get("Atualizado em")), "prazo": _iso(d.get("Prazo"))}
        elif t == "SEM PROCESSO":
            out["quadro"][rid] = {"fase": str(d.get("Fase") or "").strip() or "Em aberto",
                                  "carimbo": _iso(d.get("Atualizado em"))}
    for d in _tabela(p("documentos.json")):
        doc = str(d.get("Documento") or "").strip()
        if doc:
            out["documentos"][doc] = {"fase": fase_documento(d), "carimbo": ""}
    return out


def historico_de_fase(pasta="."):
    """Mudanças de Fase gravadas pelo app de Edição: [(iso, frente, chave, de, para)], em ordem.
    A aba Historico é lida por posição, como o app faz: Quando, Autor, Linha, Nome, Tipo, Campo, De, Para."""
    try:
        v = json.load(open(os.path.join(pasta, "historico.json"), encoding="utf-8"))
    except Exception:
        return []
    rows = v.get("values") if isinstance(v, dict) else v
    out = []
    for r in (rows or [])[1:]:
        r = list(r) + [""] * (10 - len(r))
        if str(r[5]).strip() != "Fase":
            continue
        tipo = str(r[4] or "")
        frente = tipo.split(":")[0] if ":" in tipo else "clinicas"
        q, chave = _iso(r[0]), str(r[3] or "").strip()
        if frente in FRENTES and q and chave:
            out.append((q, frente, chave, str(r[6] or "").strip(), str(r[7] or "").strip()))
    out.sort(key=lambda x: x[0])
    return out


# ---------------------------------------------------------------- regras

def etapa_de(roteiro, frente, fase):
    if frente == "documentos":
        return DOC_FASES.get(fase, 0)
    R = roteiro.get(ROT.get(frente, ""), {})
    return int((R.get("fases", {}).get(fase) or {}).get("e") or 0)


def n_etapas(roteiro, frente):
    if frente == "documentos":
        return 2
    return len(roteiro.get(ROT.get(frente, ""), {}).get("etapas", []))


def em_andamento(cfg, roteiro, frente, fase, linha=None, agora=None):
    """Item puxado e ainda não entregue: fora da fila, fora das saídas e fora da operação."""
    if fase in (cfg.get("fila", {}).get(frente) or []):
        return False
    e = etapa_de(roteiro, frente, fase)
    if e < 1 or e > n_etapas(roteiro, frente):
        return False
    # edital com prazo vencido e ainda nas etapas 1 e 2 já não é trabalho em andamento
    if frente == "licitacoes" and e < 3 and linha and linha.get("prazo") and agora:
        d = _dt(linha["prazo"])
        if d and d < agora.replace(tzinfo=None):
            return False
    return True


def percentil(v, p):
    v = sorted(v)
    if not v:
        return None
    k = (len(v) - 1) * p
    a, b = int(k), min(int(k) + 1, len(v) - 1)
    return round(v[a] + (v[b] - v[a]) * (k - a), 1)


def segunda(d):
    return (d - dt.timedelta(days=d.weekday())).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- núcleo (sem rede, testável)

def atualizar(linhas, hist, estado, trans, fotos, cfg, roteiro, agora):
    """Recebe o que já estava guardado e devolve (estado, trans_novas, fotos_novas, primeira_vez)."""
    agora_iso = agora.strftime("%Y-%m-%dT%H:%M")
    hoje = agora.strftime("%Y-%m-%d")
    primeira = not estado
    # última mudança de Fase do Historico por (frente, chave, para)
    ult = {}
    for q, f, k, de, para in hist:
        ult[(f, k, para)] = q
    novo, trans_novas = {}, []
    if primeira:
        # semente: todo o Historico de Fase vira transição, para já nascer com o passado medido
        for q, f, k, de, para in hist:
            trans_novas.append([q, f, k, de, para, "historico"])
    for f in FRENTES:
        for k, r in linhas[f].items():
            fase, ant = r["fase"], estado.get((f, k))
            if ant and ant[0] == fase:
                novo[(f, k)] = ant
                continue
            q_hist = ult.get((f, k, fase))
            if primeira:
                if q_hist:
                    novo[(f, k)] = [fase, q_hist, "historico", q_hist]
                elif r.get("carimbo"):
                    novo[(f, k)] = [fase, r["carimbo"], "carimbo", r["carimbo"]]   # no mínimo desde o último toque na linha
                else:
                    novo[(f, k)] = [fase, agora_iso, "inicio", agora_iso]          # sem registro: conta a partir de hoje
                continue
            if ant:
                exato = q_hist and q_hist > ant[1]
                q = q_hist if exato else agora_iso
                # mudou de fase dentro da mesma etapa: a entrada na etapa continua a mesma
                mesma = etapa_de(roteiro, f, ant[0]) == etapa_de(roteiro, f, fase)
                novo[(f, k)] = [fase, q, "historico" if exato else "rodada", (ant[3] or ant[1]) if mesma else q]
                # o que o app já registrou entra uma vez só
                if not any(t[1] == f and t[2] == k and t[4] == fase and t[0] == q for t in trans):
                    trans_novas.append([q, f, k, ant[0], fase, "historico" if exato else "rodada"])
            else:
                novo[(f, k)] = [fase, agora_iso, "rodada", agora_iso]
                trans_novas.append([agora_iso, f, k, "", fase, "entrada"])
    fotos_novas = []
    if not any(x[0] == hoje for x in fotos):
        cont = {}
        for (f, k), (fase, *_resto) in novo.items():
            cont[(f, fase)] = cont.get((f, fase), 0) + 1
            if em_andamento(cfg, roteiro, f, fase, linhas[f].get(k), agora):
                cont[(f, WIP)] = cont.get((f, WIP), 0) + 1
        for f in FRENTES:
            cont.setdefault((f, WIP), 0)
        fotos_novas = [[hoje, f, fase, n] for (f, fase), n in sorted(cont.items())]
    return novo, trans_novas, fotos_novas, primeira


def metricas(linhas, estado, trans, fotos, cfg, roteiro, agora):
    hoje = agora.replace(tzinfo=None)
    # tempo por etapa: estadias completas, agrupando fases seguidas da mesma etapa
    por_item = {}
    for q, f, k, de, para, _fonte in sorted(trans, key=lambda t: t[0]):
        por_item.setdefault((f, k), []).append((q, de, para))
    estadias = {}           # (frente, etapa) -> [dias]
    passagens = []          # (dia, frente, etapa_de, etapa_para)
    for (f, k), seq in por_item.items():
        ent_etapa, ent_q = None, None
        for q, de, para in seq:
            e_de, e_para = etapa_de(roteiro, f, de) if de else None, etapa_de(roteiro, f, para)
            if e_de is not None and e_de != e_para:
                passagens.append((q[:10], f, e_de, e_para))
            if ent_etapa is None:
                ent_etapa, ent_q = e_para, q
                continue
            if e_para != ent_etapa:
                a, b = _dt(ent_q), _dt(q)
                if a and b and b >= a and ent_etapa >= 1:
                    estadias.setdefault((f, ent_etapa), []).append((b - a).total_seconds() / 86400)
                ent_etapa, ent_q = e_para, q
    tempos = {}
    for (f, e), v in estadias.items():
        tempos.setdefault(f, {})[str(e)] = {"n": len(v), "p50": percentil(v, .5), "p70": percentil(v, .7),
                                            "p85": percentil(v, .85)}
    # vazão: passagens de etapa para a frente, por semana (12 semanas)
    semanas = [segunda(hoje - dt.timedelta(weeks=i)) for i in range(11, -1, -1)]
    vazao = {f: {s: [0, 0, 0] for s in semanas} for f in FRENTES}     # [avanços, entregas finais, saídas]
    for dia, f, e_de, e_para in passagens:
        d = _dt(dia)
        s = segunda(d) if d else ""
        if s not in vazao[f]:
            continue
        fim = n_etapas(roteiro, f)
        if f == "documentos":
            if e_para == 0 and e_de > 0:
                vazao[f][s][1] += 1                       # documento regularizado
            continue
        if e_para == 0:
            vazao[f][s][2] += 1                           # saiu do funil (descartado, sem retorno, perdido)
        elif e_para > e_de:
            vazao[f][s][0] += 1
            if e_para > fim:
                vazao[f][s][1] += 1                       # chegou à operação
    vaz = {f: [[s] + vazao[f][s] for s in semanas] for f in FRENTES}
    # fotos por dia e etapa (120 dias) e teto provisório (o que estava em andamento na primeira foto)
    lim_dia = (hoje - dt.timedelta(days=120)).strftime("%Y-%m-%d")
    serie, base, inicio = {}, {}, None
    for dia, f, fase, n in sorted(fotos, key=lambda x: x[0]):
        n = int(float(n or 0))
        if inicio is None:
            inicio = dia
        if fase == WIP:
            base.setdefault(f, n)
            if dia >= lim_dia:
                serie.setdefault(dia, {}).setdefault(f, {})["w"] = n
            continue
        if dia >= lim_dia and fase not in (cfg.get("fila", {}).get(f) or []):
            e = etapa_de(roteiro, f, fase)
            if 1 <= e <= n_etapas(roteiro, f):
                x = serie.setdefault(dia, {}).setdefault(f, {})
                x[str(e)] = x.get(str(e), 0) + n
    limites = {}
    for f in FRENTES:
        fixo = (cfg.get("limites") or {}).get(f)
        if fixo == 0 and fixo is not None and fixo is not False:
            limites[f] = {"n": None, "prov": False}                 # 0 = sem teto, por decisão do Marcos
        else:
            limites[f] = {"n": fixo, "prov": False} if fixo else {"n": base.get(f), "prov": True}
    # previsão por simulação: quantas passagens de etapa nas próximas semanas
    pv = cfg.get("previsao") or {}
    prev = {}
    for f in ("clinicas", "licitacoes", "quadro"):
        hist_sem = [a for _s, a, _e, _x in vaz[f][:-1]]           # a semana corrente está incompleta
        while hist_sem and hist_sem[0] == 0:                      # começa na primeira semana com registro
            hist_sem.pop(0)
        minimo = int(pv.get("semanas_minimas", 8))
        if len(hist_sem) < minimo:
            prev[f] = {"falta": minimo - len(hist_sem), "sem": len(hist_sem)}
            continue
        rnd = random.Random(f + hoje.strftime("%Y-%m-%d"))
        H, N = int(pv.get("horizonte_semanas", 4)), int(pv.get("simulacoes", 10000))
        sims = sorted(sum(rnd.choice(hist_sem) for _ in range(H)) for _ in range(N))
        # "com 85% de chance, pelo menos X": percentil 15 da distribuição
        prev[f] = {"sem": len(hist_sem), "h": H, "p50": sims[int(N * .5)], "p85": sims[int(N * .15)],
                   "p95": sims[int(N * .05)]}
    itens = {f: {k: [v[1], v[2][0], v[3] or v[1]] for (ff, k), v in estado.items() if ff == f} for f in FRENTES}
    return {"gerado": agora.strftime("%Y-%m-%dT%H:%M"), "inicio": inicio, "itens": itens, "tempos": tempos,
            "vazao": vaz, "fotos": serie, "limites": limites, "prev": prev,
            "cfg": {k: v for k, v in cfg.items() if not k.startswith("_")}}


# ---------------------------------------------------------------- guarda (planilha ou pasta local)

class Local:
    def __init__(self, pasta):
        self.p = pasta
        os.makedirs(pasta, exist_ok=True)

    def ler(self, aba):
        try:
            return json.load(open(os.path.join(self.p, aba + ".json"), encoding="utf-8"))
        except Exception:
            return []

    def gravar_tudo(self, aba, rows):
        json.dump(rows, open(os.path.join(self.p, aba + ".json"), "w", encoding="utf-8"), ensure_ascii=False)

    def acrescentar(self, aba, rows):
        self.gravar_tudo(aba, self.ler(aba) + rows)


class Planilha:
    def __init__(self):
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        info = json.loads(os.environ["GOOGLE_SA_JSON"])
        cred = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        self.api = build("sheets", "v4", credentials=cred, cache_discovery=False).spreadsheets()
        meta = self.api.get(spreadsheetId=LICIT_SHEET, fields="sheets.properties.title").execute()
        tem = {s["properties"]["title"] for s in meta.get("sheets", [])}
        for aba, cab in CAB.items():
            if aba not in tem:
                self.api.batchUpdate(spreadsheetId=LICIT_SHEET, body={"requests": [{"addSheet": {"properties": {
                    "title": aba, "gridProperties": {"frozenRowCount": 1}}}}]}).execute()
                self.api.values().update(spreadsheetId=LICIT_SHEET, range=f"{aba}!A1", valueInputOption="RAW",
                                         body={"values": [cab]}).execute()

    def ler(self, aba):
        v = self.api.values().get(spreadsheetId=LICIT_SHEET, range=f"{aba}!A2:F").execute().get("values", [])
        n = len(CAB[aba])
        return [list(r) + [""] * (n - len(r)) for r in v if r and str(r[0]).strip()]

    def gravar_tudo(self, aba, rows):
        self.api.values().clear(spreadsheetId=LICIT_SHEET, range=f"{aba}!A2:F").execute()
        for i in range(0, len(rows), 5000):
            self.api.values().update(spreadsheetId=LICIT_SHEET, range=f"{aba}!A{i + 2}", valueInputOption="RAW",
                                     body={"values": rows[i:i + 5000]}).execute()

    def acrescentar(self, aba, rows):
        for i in range(0, len(rows), 5000):
            self.api.values().append(spreadsheetId=LICIT_SHEET, range=f"{aba}!A1", valueInputOption="RAW",
                                     insertDataOption="INSERT_ROWS", body={"values": rows[i:i + 5000]}).execute()


def rodar(guarda, pasta=".", agora=None, saida="fluxo.json"):
    agora = agora or dt.datetime.now(TZ)
    cfg = json.load(open(os.path.join(RAIZ, "config", "fluxo.json"), encoding="utf-8"))
    roteiro = json.load(open(os.path.join(RAIZ, "config", "roteiro.json"), encoding="utf-8"))
    linhas = linhas_das_frentes(pasta)
    if len(linhas["clinicas"]) < 100:
        raise SystemExit(f"fluxo: leitura suspeita das clínicas ({len(linhas['clinicas'])}); nada foi gravado.")
    hist = historico_de_fase(pasta)
    estado = {(r[0], r[1]): [r[2], r[3], r[4], (r[5] if len(r) > 5 else "") or r[3]] for r in guarda.ler(ABA_ESTADO)}
    trans = guarda.ler(ABA_TRANS)
    fotos = guarda.ler(ABA_FOTOS)
    novo, trans_novas, fotos_novas, primeira = atualizar(linhas, hist, estado, trans, fotos, cfg, roteiro, agora)
    if novo != estado:
        guarda.gravar_tudo(ABA_ESTADO, [[f, k] + v for (f, k), v in sorted(novo.items())])
    if trans_novas:
        guarda.acrescentar(ABA_TRANS, trans_novas)
    if fotos_novas:
        guarda.acrescentar(ABA_FOTOS, fotos_novas)
    m = metricas(linhas, novo, trans + trans_novas, fotos + fotos_novas, cfg, roteiro, agora)
    json.dump(m, open(os.path.join(pasta, saida), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"OK fluxo: {len(novo)} itens acompanhados, {len(trans_novas)} passagens novas, "
          f"{'foto do dia guardada' if fotos_novas else 'foto do dia já existia'}"
          f"{', primeira medição (semeada pelo Historico)' if primeira else ''}")
    return m


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", default="", help="pasta para guardar o estado em json (teste, sem planilha)")
    a = ap.parse_args()
    try:
        rodar(Local(a.local) if a.local else Planilha())
    except SystemExit:
        raise
    except Exception as e:      # nunca derruba a rodada
        print(f"::warning::A medição do fluxo falhou nesta rodada: {e}")
        sys.exit(0)
