#!/usr/bin/env python3
"""Central TRX: gera dados_central.js a partir das planilhas-fonte.

Uso:
  python3 build_central.py --pipeline PIPELINE.json --licitacoes Pipeline_Licitacoes.xlsx \
      --saida dados_central.js [--mod-pipeline ISO] [--mod-licitacoes ISO]

PIPELINE.json: resultado de get_values("Pipeline!A1:AP") do conector Google Sheets
  (objeto com a chave "values", ou a própria lista de linhas).
Pipeline_Licitacoes.xlsx: arquivo baixado do Drive (base64 já decodificado).

A página só mostra dados. Telefone, WhatsApp e e-mail não entram: o contato
continua na planilha, que é a fonte da verdade.
"""
import argparse, datetime as dt, html, json, re, sys, unicodedata

TZ = dt.timezone(dt.timedelta(hours=-3))
PIPELINE_ID = "1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0"
PIPELINE_GID = 1118277134
LICIT_ID = "1FTHl-0FePl8aSIwGEuzFAj-P1GWEx_H1"
LICIT_SHEET = "1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8"
LICIT_GID = 1773203614


def txt(v, lim=None):
    if v is None:
        return ""
    s = str(v)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    if lim and len(s) > lim:
        s = s[: lim - 1].rstrip() + "…"
    return s


def num(v):
    if v is None or v == "":
        return None
    s = str(v).strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def data_iso(v):
    """Aceita datetime, 'DD/MM/AAAA', 'DD/MM/AAAA HH:MM' ou 'AAAA-MM-DD'."""
    if v is None or v == "":
        return ""
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%dT%H:%M")
    if isinstance(v, dt.date):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?", s)
    if m:
        d, mo, y, h, mi = m.groups()
        return f"{y}-{mo}-{d}" + (f"T{int(h):02d}:{mi}" if h else "")
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?", s)
    if m:
        y, mo, d, h, mi = m.groups()
        return f"{y}-{mo}-{d}" + (f"T{h}:{mi}" if h else "")
    return ""


def clinicas(values):
    H = values[0]
    col = {h: i for i, h in enumerate(H) if h}
    def g(r, name, lim=None):
        i = col.get(name)
        return txt(r[i], lim) if i is not None and i < len(r) else ""
    out = []
    for n, r in enumerate(values[1:], start=2):
        if not r or not str(r[0]).strip():
            continue
        out.append({
            "l": n,
            "n": g(r, "Clinica"),
            "c": g(r, "Cidade"),
            "uf": g(r, "UF"),
            "pr": g(r, "Prioridade").upper(),
            "mod": g(r, "Modalidades", 160),
            "g": g(r, "Gancho", 420),
            "resp": g(r, "Responsavel"),
            "fase": g(r, "Fase") or "Sem fase",
            "toque": g(r, "Toque_atual"),
            "prox": data_iso(g(r, "Proximo_toque")),
            "ini": data_iso(g(r, "Inicio_cadencia")),
            "ult": data_iso(g(r, "Ultima_atualizacao")),
            "res": g(r, "Resultado", 200),
            "notas": g(r, "Notas", 420),
            "acao": g(r, "Proxima_Acao", 200),
            "sc": num(g(r, "Score")),
            "fx": g(r, "Faixa") or "SEM MEDICAO",
            "dor": num(g(r, "Dor")),
            "cob": g(r, "Cobertura"),
            "jan": num(g(r, "Janela")),
            "perf": num(g(r, "Perfil")),
            "sjan": g(r, "Sinal_de_compra", 300),
            "nec": num(g(r, "Necessidade")),
            "snec": g(r, "Sinal_operacional", 200),
            "ra": g(r, "Nota_RA", 160),
            "ggl": g(r, "Nota_Google"),
            "oq": g(r, "O_que_reclamam", 360),
            "med": data_iso(g(r, "Medido_em")),
        })
    return out


def abas_licitacoes(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    res = {}
    for aba in ("CREDENCIAMENTO", "PREGAO", "SEM PROCESSO", "DESCARTADOS"):
        if aba not in wb.sheetnames:
            res[aba] = []
            continue
        rows = list(wb[aba].iter_rows(values_only=True))
        hi = next((i for i, r in enumerate(rows) if r and sum(1 for c in r if c) > 5), 0)
        H = [str(h).strip() if h else "" for h in rows[hi]]
        res[aba] = [(i + hi + 2, dict(zip(H, r))) for i, r in enumerate(rows[hi + 1:]) if r and any(r)]
    return res


def abas_da_planilha(path):
    """licitacoes.json (get_values da aba Licitacoes) agrupado pela coluna Trilha."""
    pv = json.load(open(path, encoding="utf-8"))
    rows = pv["values"] if isinstance(pv, dict) else pv
    H = [str(h).strip() for h in rows[0]]
    res = {k: [] for k in ("CREDENCIAMENTO", "PREGAO", "SEM PROCESSO", "DESCARTADOS", "ENCERRADO")}
    for n, r in enumerate(rows[1:], start=2):
        d = dict(zip(H, r + [""] * (len(H) - len(r))))
        t = str(d.get("Trilha") or "").strip()
        if t in res and str(d.get("ID") or "").strip():
            res[t].append((n, d))
    return res


def licitacao(linha, d, aba):
    return {
        "l": linha, "aba": aba,
        "id": txt(d.get("ID")),
        "fase": txt(d.get("Fase")) or "Mapeado",
        "enc": txt(d.get("Encaixe")).lower(),
        "sc": num(d.get("Score")),
        "fx": txt(d.get("Faixa")),
        "prazo": data_iso(d.get("Prazo")),
        "org": txt(d.get("Orgao"), 140),
        "c": txt(d.get("Cidade")),
        "uf": txt(d.get("UF")),
        "mod": txt(d.get("Modalidade")),
        "ed": txt(d.get("Edital"), 120),
        "obj": txt(d.get("Objeto"), 420),
        "val": num(d.get("Valor estimado")),
        "onde": txt(d.get("Onde disputa"), 80),
        "bloq": txt(d.get("Bloqueio"), 220),
        "acao": txt(d.get("Proxima acao"), 220),
        "qd": data_iso(d.get("Quando")),
        "resp": txt(d.get("Responsavel")),
        "notas": txt(d.get("Notas da Carla"), 360),
        "res": txt(d.get("Resultado"), 160),
        "led": txt(d.get("Link edital")) if str(d.get("Link edital") or "").startswith("http") else "",
        "lpn": txt(d.get("Link PNCP")) if str(d.get("Link PNCP") or "").startswith("http") else "",
        "pasta": txt(d.get("Pasta do processo")) if str(d.get("Pasta do processo") or "").startswith("http") else "",
        "at": data_iso(d.get("Atualizado em")),
        "jan": num(d.get("Eixo Janela")), "sjan": txt(d.get("Sinal de compra"), 200),
        "nec": num(d.get("Eixo Necessidade")), "snec": txt(d.get("Sinal operacional"), 200),
        "dorx": num(d.get("Eixo Dor")), "oq": txt(d.get("O que reclamam"), 240),
        "cob": txt(d.get("Cobertura")), "med": data_iso(d.get("Medido em")),
    }


def quadro(linha, d):
    return {
        "l": linha,
        "id": txt(d.get("ID")),
        "sit": txt(d.get("Situacao do envio")) or "Sem situação",
        "fase": txt(d.get("Fase")) or "Em aberto",
        "enc": txt(d.get("Encaixe")).lower(),
        "sc": num(d.get("Score")),
        "fx": txt(d.get("Faixa")) or "SEM MEDICAO",
        "org": txt(d.get("Orgao"), 140),
        "c": txt(d.get("Cidade")),
        "uf": txt(d.get("UF")),
        "obj": txt(d.get("Objeto"), 300),
        "bloq": txt(d.get("Bloqueio"), 160),
        "cargo": txt(d.get("Cargo"), 60),
        "acao": txt(d.get("Proxima acao"), 160),
        "resp": txt(d.get("Responsavel")),
        "notas": txt(d.get("Notas da Carla"), 300),
        "at": data_iso(d.get("Atualizado em")),
        "jan": num(d.get("Eixo Janela")), "sjan": txt(d.get("Sinal de compra"), 200),
        "nec": num(d.get("Eixo Necessidade")), "snec": txt(d.get("Sinal operacional"), 200),
        "dorx": num(d.get("Eixo Dor")), "oq": txt(d.get("O que reclamam"), 240),
        "cob": txt(d.get("Cobertura")), "med": data_iso(d.get("Medido em")),
    }


DOCS_SHEET = "13nXaAsgQ4czDGnp6SZd2ConSeV_8_1exZG_lH4l9hD8"
DOCS_GID = 423972086


def link_http(v):
    """So deixa passar link http(s). Celula com texto solto vira vazio."""
    u = txt(v, 600)
    return u if u.startswith("http://") or u.startswith("https://") else ""


def isgh_dossie(path):
    """Aba ISGH_Dossie da Pipeline Licitacoes (Secao|Titulo|Texto|Link|Ordem), 09/11/2026.
    O detalhe do contrato HRVJ/ISGH dentro da propria Central: a equipe abre a aba ISGH em vez
    de depender de um artefato fora dela. Dentro de cada secao vale a coluna Ordem e, empatando,
    a ordem das linhas. Sem aba ou vazia, devolve [] e a aba nao aparece."""
    try:
        pv = json.load(open(path, encoding="utf-8"))
        rows = pv["values"] if isinstance(pv, dict) else pv
    except Exception:
        return []
    if not rows or len(rows) < 2:
        return []
    H = [str(h).strip() for h in rows[0]]
    out = []
    for i, r in enumerate(rows[1:]):
        d = dict(zip(H, list(r) + [""] * (len(H) - len(r))))
        sec = txt(d.get("Secao"))
        ttl = txt(d.get("Titulo"), 160)
        if not sec or not ttl:
            continue
        try:
            ordem = int(float(str(d.get("Ordem", "")).replace(",", ".").strip()))
        except (TypeError, ValueError):
            ordem = 9999
        out.append({"sec": sec, "t": ttl, "x": txt(d.get("Texto"), 1400),
                    "lk": link_http(d.get("Link")), "_o": ordem, "_i": i})
    out.sort(key=lambda it: (it["_o"], it["_i"]))
    for it in out:
        it.pop("_o", None)
        it.pop("_i", None)
    return out


def destaque_isgh(path):
    """Aba Destaque_ISGH da Pipeline Licitacoes (Secao|Titulo|Texto|Prazo|Dono|Ordem).
    Prioridade maxima ISGH definida pelo Marcos em 08/11/2026. Sem aba ou vazia, devolve [].
    Ordem (09/11/2026): dentro de cada secao vale primeiro a coluna Ordem, depois o Prazo mais
    proximo; item sem prazo vai para o fim. Antes a lista saia na ordem das linhas da planilha e
    as datas apareciam embaralhadas. O Texto vai ate 700 caracteres: as mensagens prontas para a
    equipe enviar nao cabiam em 300 e apareciam cortadas no meio da frase."""
    try:
        pv = json.load(open(path, encoding="utf-8"))
        rows = pv["values"] if isinstance(pv, dict) else pv
    except Exception:
        return []
    if not rows or len(rows) < 2:
        return []
    H = [str(h).strip() for h in rows[0]]
    out = []
    for i, r in enumerate(rows[1:]):
        d = dict(zip(H, list(r) + [""] * (len(H) - len(r))))
        sec = txt(d.get("Secao"))
        if not sec:
            continue
        try:
            ordem = int(float(str(d.get("Ordem", "")).replace(",", ".").strip()))
        except (TypeError, ValueError):
            ordem = 9999
        out.append({"sec": sec, "t": txt(d.get("Titulo"), 160), "x": txt(d.get("Texto"), 700),
                    "dt": data_iso(d.get("Prazo")) or "", "resp": txt(d.get("Dono"), 40),
                    "lk": link_http(d.get("Link")), "_o": ordem, "_i": i})
    out.sort(key=lambda it: (it["_o"], it["dt"] or "9999-12-31", it["_i"]))
    for it in out:
        it.pop("_o", None)
        it.pop("_i", None)
    return out


def documentos_alerta(path):
    """Documentos TRX: tudo que tem validade e pede acao. Vermelho: VENCEU (Status VENCIDO)
    ou DESATUALIZADO (coluna T preenchida). Laranja: Status VENCE EM ... (15/30/45 dias),
    para a Carla renovar antes de travar (decisao do Marcos em 04/11/2026)."""
    try:
        dv = json.load(open(path, encoding="utf-8"))
    except Exception:
        return []
    rows = dv["values"] if isinstance(dv, dict) else dv
    if not rows:
        return []
    H = [str(h).strip() for h in rows[0]]
    out = []
    for n, r in enumerate(rows[1:], start=2):
        d = dict(zip(H, r + [""] * (len(H) - len(r))))
        doc = txt(d.get("Documento"), 140)
        if not doc:
            continue
        status = str(d.get("Status") or "").strip().upper()
        venc = status == "VENCIDO"
        breve = status if status.startswith("VENCE EM") else ""
        desat = txt(d.get("Desatualizado (motivo)"), 220)
        if not venc and not desat and not breve:
            continue
        out.append({"l": n, "doc": doc, "venc": venc, "breve": breve, "val": data_iso(d.get("Validade")),
                    "mot": desat, "resp": txt(d.get("Responsavel")), "sit": txt(d.get("Situacao"), 60)})
    out.sort(key=lambda x: (0 if x["venc"] else (1 if x["mot"] else 2), x["val"] or "9999"))
    return out


PROD_GID = 1397135487          # aba Producao_Socios da Pipeline Licitacoes
PARAMS_GID = 1912529267        # aba Producao_Params (a regua)
ESCALA_GID = 1455089774        # aba Escala_Socios

# Modalidade: o sistema do hospital escreve o codigo DICOM (MR, CT, CR), a equipe escreve a sigla.
MOD_ALIAS = {"MR": "RM", "RM": "RM", "CT": "TC", "TC": "TC", "CR": "RX", "DX": "RX", "DR": "RX",
             "RX": "RX", "MG": "MMG", "MMG": "MMG", "US": "US", "BMD": "DO", "DO": "DO"}
# Unidade de esforco por modalidade. Padrao da regua aprovada em 01/09/2026 (1 TC = 3 MMG = 4 RX);
# a RM nao tinha coeficiente e entra como proposta de 1,5 TC. Tudo isso e sobreposto pela
# aba Producao_Params, que e quem manda.
COEF_PADRAO = {"RM": 1.5, "TC": 1.0, "MMG": 1.0 / 3, "RX": 0.25, "US": 0.5, "DO": 0.25}
PESO_PADRAO = {"esforco": 40.0, "prazo": 25.0, "margem": 20.0, "escala": 15.0}
META_MARGEM_PADRAO = 0.09      # regra do Marcos de 23/10/2026: lucro de 9% do faturamento
# Fator liquido do contrato privado: 9% de impostos, 10% de gestao e 1% do programador
# ([[custos-fixos-trx-2026-10]], 05/11/2026). A margem do eixo sai da receita JA liquida
# dessas deducoes, senao todo laudo pareceria render 40%.
FATOR_LIQUIDO_PADRAO = 0.8099
PENA_NAO_COBERTO = 15.0        # pontos descontados do eixo escala por escala devolvida


def _tab(rows):
    """Lista de listas da planilha -> lista de dicionarios pelo cabecalho da linha 1."""
    if not rows or len(rows) < 2:
        return []
    H = [str(h).strip() for h in rows[0]]
    out = []
    for n, r in enumerate(rows[1:], start=2):
        r = list(r) + [""] * (len(H) - len(r))
        d = {h: r[i] for i, h in enumerate(H) if h}
        d["_l"] = n
        out.append(d)
    return out


def _sim(v):
    return str(v).strip().lower() in ("sim", "s", "true", "1", "x", "socio", "sócio")


def producao_socios(path):
    """Abas Producao_Params, Producao_Socios e Escala_Socios da Pipeline Licitacoes (11/11/2026).

    Devolve o coeficiente de esforco e o score de cada medico por periodo. O score e a media
    ponderada de quatro eixos, com os pesos da aba Producao_Params:
      esforco  volume convertido em unidade de esforco (UE) contra a meta ou a media dos socios;
      prazo    porcentagem de laudos entregues dentro do SLA, contado da atribuicao;
      margem   (receita - repasse) / receita do que a pessoa laudou, contra a meta de margem;
      escala   plantoes e sobreavisos assumidos, menos desconto por escala devolvida.
    Eixo sem dado no periodo SAI da conta e o peso dele e redistribuido entre os eixos medidos:
    assim a Central ja serve antes de a aba de escala estar preenchida. Sem as abas, devolve {}.
    """
    try:
        pv = json.load(open(path, encoding="utf-8"))
    except Exception:
        return {}
    params_rows = pv.get("params") or []
    prod_rows = pv.get("producao") or []
    escala_rows = pv.get("escala") or []
    if not prod_rows or len(prod_rows) < 2:
        return {}

    # ---- a regua
    par = {}
    for d in _tab(params_rows):
        k = txt(d.get("Chave")).strip()
        if not k:
            continue
        par[k.lower()] = d.get("Valor")
    coef = dict(COEF_PADRAO)
    for k, v in par.items():
        if k.startswith("coef_"):
            sigla = MOD_ALIAS.get(k[5:].upper(), k[5:].upper())
            n = num(v)
            if n is not None and n > 0:
                coef[sigla] = n
    pesos = {}
    for eixo, padrao in PESO_PADRAO.items():
        n = num(par.get("peso_" + eixo))
        pesos[eixo] = padrao if n is None else max(0.0, n)
    meta_margem = num(par.get("meta_margem"))
    if meta_margem is None or meta_margem <= 0:
        meta_margem = META_MARGEM_PADRAO
    if meta_margem > 1:
        meta_margem = meta_margem / 100.0
    fator_liq = num(par.get("fator_liquido"))
    if fator_liq is None or not (0 < fator_liq <= 1):
        fator_liq = FATOR_LIQUIDO_PADRAO
    meta_ue = num(par.get("meta_ue_mes"))
    meta_pl = num(par.get("meta_plantoes_mes"))
    teto = num(par.get("teto_nota")) or 100.0
    sla = {"urgencia": num(par.get("sla_urgencia_h")) or 2.0,
           "internado": num(par.get("sla_internado_h")) or 12.0,
           "ambulatorial": num(par.get("sla_ambulatorial_h")) or 48.0}

    # ---- lancamentos
    gente = {}

    def pega(per, nome):
        k = (per, nome)
        if k not in gente:
            gente[k] = {"per": per, "n": nome, "socio": False, "ex": 0, "ue": 0.0, "pz": 0,
                        "pz_base": 0, "rec": 0.0, "rep": 0.0, "mods": {}, "ctr": set(),
                        "pl": None, "sob": None, "ncob": 0, "obs": "", "l": None, "hrs": []}
        return gente[k]

    for d in _tab(prod_rows):
        per = txt(d.get("Periodo"))[:7]
        nome = txt(d.get("Medico"), 60)
        if not per or not nome:
            continue
        ex = num(d.get("Exames")) or 0
        if ex <= 0:
            continue
        mod = MOD_ALIAS.get(txt(d.get("Modalidade")).upper(), txt(d.get("Modalidade")).upper())
        fator = num(d.get("Fator"))
        fator = 1.0 if fator is None or fator <= 0 else fator
        g = pega(per, nome)
        g["socio"] = g["socio"] or _sim(d.get("Socio"))
        g["ex"] += int(ex)
        g["ue"] += ex * coef.get(mod, 1.0) * fator
        pz = num(d.get("No_prazo"))
        if pz is not None and str(d.get("No_prazo")).strip() != "":
            g["pz"] += int(pz)
            g["pz_base"] += int(ex)
        g["rec"] += num(d.get("Receita")) or 0.0
        g["rep"] += num(d.get("Repasse")) or 0.0
        h = num(d.get("Horas_medianas"))
        if h is not None:
            g["hrs"].append((h, int(ex)))
        m = g["mods"].setdefault(mod, {"m": mod, "ex": 0, "ue": 0.0})
        m["ex"] += int(ex)
        m["ue"] += ex * coef.get(mod, 1.0) * fator
        ctr = txt(d.get("Contrato"), 40)
        if ctr:
            g["ctr"].add(ctr)
        if not g["obs"]:
            g["obs"] = txt(d.get("Obs"), 220)
        if g["l"] is None:
            g["l"] = d["_l"]

    for d in _tab(escala_rows):
        per = txt(d.get("Periodo"))[:7]
        nome = txt(d.get("Medico"), 60)
        if not per or not nome:
            continue
        pl, sob, nc = num(d.get("Plantoes")), num(d.get("Sobreavisos")), num(d.get("Nao_cobertos"))
        if pl is None and sob is None and nc is None:
            continue
        g = pega(per, nome)
        g["pl"] = (g["pl"] or 0) + (pl or 0)
        g["sob"] = (g["sob"] or 0) + (sob or 0)
        g["ncob"] += int(nc or 0)

    # ---- notas por periodo
    def nota(valor, ref, meta):
        """Com meta: 100 quando bate a meta. Sem meta: 50 na media dos socios, 100 no dobro."""
        if meta and meta > 0:
            return min(teto, 100.0 * valor / meta)
        if not ref or ref <= 0:
            return None
        return min(teto, 50.0 * valor / ref)

    periodos = []
    for per in sorted({k[0] for k in gente}, reverse=True):
        linhas = [g for k, g in gente.items() if k[0] == per]
        socios = [g for g in linhas if g["socio"]]
        base = socios or linhas
        ue_med = (sum(g["ue"] for g in base) / len(base)) if base else 0.0
        pl_base = [g for g in base if g["pl"] is not None or g["sob"] is not None]
        pl_med = (sum((g["pl"] or 0) + (g["sob"] or 0) for g in pl_base) / len(pl_base)) if pl_base else 0.0
        ue_socios = sum(g["ue"] for g in socios) or sum(g["ue"] for g in linhas)
        saida = []
        for g in sorted(linhas, key=lambda x: -x["ue"]):
            liq = g["rec"] * fator_liq
            margem_pct = ((liq - g["rep"]) / g["rec"]) if g["rec"] else None
            notas = {
                "esforco": nota(g["ue"], ue_med, meta_ue),
                "prazo": (100.0 * g["pz"] / g["pz_base"]) if g["pz_base"] else None,
                "margem": (max(0.0, min(teto, 100.0 * margem_pct / meta_margem))
                           if margem_pct is not None else None),
                "escala": None,
            }
            if g["pl"] is not None or g["sob"] is not None:
                bruto = nota((g["pl"] or 0) + (g["sob"] or 0), pl_med, meta_pl)
                if bruto is not None:
                    notas["escala"] = max(0.0, bruto - PENA_NAO_COBERTO * g["ncob"])
            vivos = {e: v for e, v in notas.items() if v is not None}
            soma_peso = sum(pesos[e] for e in vivos) or 0.0
            score = (sum(notas[e] * pesos[e] for e in vivos) / soma_peso) if soma_peso else None
            hrs = (sum(h * n for h, n in g["hrs"]) / sum(n for _, n in g["hrs"])) if g["hrs"] else None
            saida.append({
                "n": g["n"], "socio": g["socio"], "ex": g["ex"], "ue": round(g["ue"], 1),
                "share": round(100.0 * g["ue"] / ue_socios, 1) if ue_socios and g["socio"] else None,
                "pz": g["pz"], "pzb": g["pz_base"],
                "pzp": round(100.0 * g["pz"] / g["pz_base"], 1) if g["pz_base"] else None,
                "hrs": round(hrs, 1) if hrs is not None else None,
                "rec": round(g["rec"], 2), "recl": round(liq, 2), "rep": round(g["rep"], 2),
                "mg": round(liq - g["rep"], 2),
                "mgp": round(100.0 * margem_pct, 1) if margem_pct is not None else None,
                "pl": g["pl"], "sob": g["sob"], "ncob": g["ncob"],
                "notas": {e: (round(v, 1) if v is not None else None) for e, v in notas.items()},
                "score": round(score, 1) if score is not None else None,
                "mods": sorted(({"m": m["m"], "ex": m["ex"], "ue": round(m["ue"], 1)}
                                for m in g["mods"].values()), key=lambda x: -x["ue"]),
                "ctr": sorted(g["ctr"]), "obs": g["obs"], "l": g["l"],
            })
        falta = [e for e in PESO_PADRAO if all(x["notas"][e] is None for x in saida)]
        periodos.append({
            "per": per,
            "medicos": saida,
            "tot": {"ex": sum(x["ex"] for x in saida), "ue": round(sum(x["ue"] for x in saida), 1),
                    "rec": round(sum(x["rec"] for x in saida), 2),
                    "rep": round(sum(x["rep"] for x in saida), 2),
                    "socios": len([x for x in saida if x["socio"]]),
                    "parceiros": len([x for x in saida if not x["socio"]]),
                    "pzp": (round(100.0 * sum(x["pz"] for x in saida) / sum(x["pzb"] for x in saida), 1)
                            if sum(x["pzb"] for x in saida) else None),
                    "repm": (round(sum(x["rep"] for x in saida) / sum(x["ex"] for x in saida), 2)
                             if sum(x["ex"] for x in saida) else None),
                    "mg": round(sum(x["mg"] for x in saida), 2),
                    "mgp": (round(100.0 * sum(x["mg"] for x in saida) / sum(x["rec"] for x in saida), 1)
                            if sum(x["rec"] for x in saida) else None)},
            "ref": {"ue_med": round(ue_med, 1), "pl_med": round(pl_med, 1)},
            "falta": falta,
        })

    return {"periodos": periodos,
            "regua": {"coef": {k: round(v, 4) for k, v in sorted(coef.items(), key=lambda x: -x[1])},
                      "pesos": pesos, "meta_margem": meta_margem, "fator_liq": fator_liq,
                      "meta_ue": meta_ue,
                      "meta_pl": meta_pl, "sla": sla, "pena": PENA_NAO_COBERTO},
            "fonte": {"id": LICIT_SHEET, "gid": PROD_GID, "params_gid": PARAMS_GID,
                      "escala_gid": ESCALA_GID}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", required=True)
    ap.add_argument("--licitacoes", required=True, help="xlsx do robô (reserva) ou licitacoes.json da planilha Google")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--mod-pipeline", default="")
    ap.add_argument("--mod-licitacoes", default="")
    ap.add_argument("--documentos", default="", help="documentos.json (aba Documentos da planilha Documentos TRX)")
    ap.add_argument("--destaque", default="", help="destaque_isgh.json (aba Destaque_ISGH da Pipeline Licitacoes)")
    ap.add_argument("--dossie", default="", help="isgh_dossie.json (aba ISGH_Dossie da Pipeline Licitacoes)")
    ap.add_argument("--producao", default="", help="producao.json (abas Producao_Params, Producao_Socios e Escala_Socios)")
    a = ap.parse_args()

    pv = json.load(open(a.pipeline, encoding="utf-8"))
    values = pv["values"] if isinstance(pv, dict) else pv
    cl = clinicas(values)
    da_planilha = a.licitacoes.endswith(".json")
    ab = abas_da_planilha(a.licitacoes) if da_planilha else abas_licitacoes(a.licitacoes)
    lic = [licitacao(l, d, "CREDENCIAMENTO") for l, d in ab["CREDENCIAMENTO"]] + \
          [licitacao(l, d, "PREGAO") for l, d in ab["PREGAO"]]
    qd = [quadro(l, d) for l, d in ab["SEM PROCESSO"]]

    if len(cl) < 100 or len(qd) < 100:
        sys.exit(f"ERRO: leitura suspeita (clinicas={len(cl)}, quadro={len(qd)}). Nada foi gerado.")

    agora = dt.datetime.now(TZ)
    # processos que encerraram nos últimos 10 dias sem Resultado: a equipe registra o que houve
    lim = (agora - dt.timedelta(days=10)).strftime("%Y-%m-%d")
    enc_rec = [licitacao(l, d, "ENCERRADO") for l, d in ab.get("ENCERRADO", [])]
    enc_rec = sorted([e for e in enc_rec if e["prazo"] and e["prazo"][:10] >= lim and not e["res"]],
                     key=lambda e: e["prazo"], reverse=True)
    # tudo que tem Resultado registrado (licitações de qualquer trilha e clínicas)
    resultados = []
    pv2 = json.load(open(a.licitacoes, encoding="utf-8")) if da_planilha else None
    if pv2:
        rows = pv2["values"] if isinstance(pv2, dict) else pv2
        H2 = [str(h).strip() for h in rows[0]]
        for n, r in enumerate(rows[1:], start=2):
            d = dict(zip(H2, r + [""] * (len(H2) - len(r))))
            res = txt(d.get("Resultado"), 220)
            if res and str(d.get("ID") or "").strip() and not res.startswith("Ruído do radar"):
                resultados.append({"src": "quadro" if str(d.get("Trilha")) == "SEM PROCESSO" else "licitacoes",
                                   "l": n, "n": txt(d.get("Orgao"), 140) or txt(d.get("ID")), "uf": txt(d.get("UF")),
                                   "tp": txt(d.get("Modalidade")) or txt(d.get("Trilha")), "fase": txt(d.get("Fase")),
                                   "res": res, "dt": data_iso(d.get("Prazo")), "resp": txt(d.get("Responsavel"))})
    for c in cl:
        if c.get("res"):
            resultados.append({"src": "clinicas", "l": c["l"], "n": c["n"], "uf": c["uf"], "tp": "Clínica",
                               "fase": c["fase"], "res": c["res"], "dt": c.get("ult", ""), "resp": c["resp"]})
    dados = {
        "gerado": agora.strftime("%Y-%m-%dT%H:%M"),
        "fontes": {
            "pipeline": {"nome": "Pipeline TRX — Prospecção (fonte da verdade)", "id": PIPELINE_ID,
                          "gid": PIPELINE_GID, "mod": a.mod_pipeline, "linhas": len(cl)},
            "licitacoes": {"nome": "Pipeline Licitações TRX (fonte da verdade)" if da_planilha else "Pipeline_Licitacoes.xlsx",
                            "id": LICIT_SHEET if da_planilha else LICIT_ID, "gid": LICIT_GID if da_planilha else None,
                            "sheet": da_planilha, "mod": a.mod_licitacoes,
                            "linhas": len(lic), "quadro": len(qd), "descartados": len(ab["DESCARTADOS"]),
                            "encerrados": len(ab.get("ENCERRADO", []))},
        },
        "clinicas": cl,
        "licitacoes": lic,
        "quadro": qd,
        "encerrados_recentes": enc_rec,
        "resultados": resultados,
        "documentos_alerta": documentos_alerta(a.documentos) if a.documentos else [],
        "destaque_isgh": destaque_isgh(a.destaque) if a.destaque else [],
        "isgh_dossie": isgh_dossie(a.dossie) if a.dossie else [],
        "producao_socios": producao_socios(a.producao) if a.producao else {},
        "documentos_fonte": {"id": DOCS_SHEET, "gid": DOCS_GID},
    }
    js = "window.CENTRAL=" + json.dumps(dados, ensure_ascii=False, separators=(",", ":")) + ";\n"
    open(a.saida, "w", encoding="utf-8").write(js)
    print(f"OK {a.saida}: {len(cl)} clinicas, {len(lic)} licitacoes, {len(qd)} municipios do quadro, "
          f"{len(js)//1024} KB, gerado {dados['gerado']}")


if __name__ == "__main__":
    main()
