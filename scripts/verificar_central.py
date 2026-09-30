#!/usr/bin/env python3
"""Verificação automática da Central TRX. Roda no GitHub depois de gerar a página.

Confere se os motores estão vivos e se os dados das duas planilhas batem com as regras:
  - frescor: xlsx do robô do Mac, Pipeline e planilha de licitações;
  - clínicas: Score e Faixa pela régua privada, duplicadas, ativas sem medição;
  - licitações: IDs repetidos, Trilha, Score e Faixa pela régua pública, prazos perto
    de vencer sem ninguém cuidando (oportunidade em risco).
Saída: avisos no Actions (::warning / ::notice), resumo da rodada e site/saude.js
(window.SAUDE), que a página mostra no topo quando há alerta.
Nunca derruba a publicação: sai sempre com código 0.
"""
import datetime as dt, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sincronizar_licitacoes import (slug, trilha_de, classificar_publico, medido, prazo_passou,  # noqa: E402
                                    ORIGENS_NUVEM)

TZ = dt.timezone(dt.timedelta(hours=-3))
AGORA = dt.datetime.now(TZ)
INATIVAS = ("descartad", "sem retorno", "fechad", "perdid")
FASES_PARADAS = {"", "mapeado", "lendo edital", "em aberto"}


def env():
    d = {}
    if os.path.exists("mods.env"):
        for l in open("mods.env"):
            if "=" in l:
                k, v = l.strip().split("=", 1)
                d[k] = v
    return d


def horas_desde(iso):
    try:
        t = dt.datetime.fromisoformat(iso).replace(tzinfo=TZ)
        return (AGORA - t).total_seconds() / 3600
    except Exception:
        return None


def num(v):
    try:
        s = str(v).strip().replace(",", ".")
        return float(s) if s != "" else None
    except ValueError:
        return None


def tabela(path):
    v = json.load(open(path, encoding="utf-8"))
    v = v["values"] if isinstance(v, dict) else v
    H = [str(h).strip() for h in v[0]]
    out = []
    for n, r in enumerate(v[1:], start=2):
        r = list(r) + [""] * (len(H) - len(r))
        out.append((n, {h: r[i] for i, h in enumerate(H) if h}))
    return out


def faixa(sc):
    return "ATACAR AGORA" if sc >= 70 else "QUENTE" if sc >= 50 else "MORNO" if sc >= 30 else "FRIO"


def privada(r):
    """Régua da clínica privada: 30% Janela, 45% Necessidade, 25% Dor; tetos 69/45/75."""
    j, n, d = num(r.get("Janela")), num(r.get("Necessidade")), num(r.get("Dor"))
    med = [(p, x) for p, x in ((0.30, j), (0.45, n), (0.25, d)) if x is not None]
    if not med:
        return None
    sc = sum(p * x for p, x in med) / sum(p for p, _ in med)
    if j is None: sc = min(sc, 69)
    if j is None and n is None: sc = min(sc, 45)
    if j is not None and n is None and d is None: sc = min(sc, 75)
    return int(math.floor(sc + 0.5))


def data_br(s):
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", str(s or ""))
    return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def main():
    alertas, avisos, info = [], [], {}
    m = env()

    # 1. Frescor dos motores
    for chave, nome, limite in (("MOD_LICIT", "Pipeline_Licitacoes.xlsx (robô do Mac: radar, quadro, e-mail)", 30),
                                ("MOD_PIPELINE", "Pipeline TRX (clínicas)", 72),
                                ("MOD_LICIT_SHEET", "Pipeline Licitações TRX (planilha Google)", 30)):
        h = horas_desde(m.get(chave, ""))
        info[chave] = m.get(chave, "")
        if h is None:
            avisos.append(f"Não consegui ler a data de {nome}.")
        elif h > limite:
            alertas.append(f"{nome} sem atualização há {int(h)}h. O motor que grava nele pode ter parado.")

    # 2. Clínicas
    cl = tabela("pipeline.json")
    ativas = [(n, r) for n, r in cl if str(r.get("Clinica") or "").strip()
              and not str(r.get("Fase") or "").strip().lower().startswith(INATIVAS)]
    sem_med = [n for n, r in ativas if privada(r) is None]
    divergentes = []
    for n, r in ativas:
        sc = privada(r)
        atual = num(r.get("Score"))
        if sc is not None and (atual is None or abs(atual - sc) > 1 or str(r.get("Faixa") or "") != faixa(sc)):
            divergentes.append(n)
    chaves = {}
    for n, r in cl:
        k = (re.sub(r"\W+", "", str(r.get("Clinica") or "").lower()), str(r.get("Cidade") or "").strip().lower())
        if k[0]:
            chaves.setdefault(k, []).append(n)
    dup = [v for v in chaves.values() if len(v) > 1]
    info["clinicas"] = {"total": len(cl), "ativas": len(ativas), "sem_medicao": len(sem_med),
                        "score_divergente": len(divergentes), "duplicadas": len(dup)}
    if divergentes:
        alertas.append(f"{len(divergentes)} clínicas com Score ou Faixa fora da régua (linhas {', '.join(map(str, divergentes[:12]))}).")
    if dup:
        avisos.append(f"{len(dup)} clínicas repetidas na Pipeline (linhas {'; '.join('/'.join(map(str, d)) for d in dup[:8])}).")
    if sem_med:
        avisos.append(f"{len(sem_med)} clínicas ativas ainda sem nenhum eixo medido.")

    # 3. Licitações
    lic = tabela("licitacoes.json")
    ids = {}
    for n, r in lic:
        rid = str(r.get("ID") or "").strip()
        if rid:
            ids.setdefault(rid, []).append(n)
    rep = {k: v for k, v in ids.items() if len(v) > 1}
    trilha_errada, score_errado, risco, sem_prazo = [], [], [], []
    hoje = AGORA.date()
    for n, r in lic:
        t = str(r.get("Trilha") or "")
        if t == "ARQUIVADO":
            continue
        if trilha_de(r) != t:
            trilha_errada.append(n)
        if medido(r):
            sc, fx, _ = classificar_publico(r, t)
            if sc is not None and (num(r.get("Score")) != sc or str(r.get("Faixa") or "") != fx):
                score_errado.append(n)
        if t in ("CREDENCIAMENTO", "PREGAO"):
            p = data_br(r.get("Prazo"))
            fase = str(r.get("Fase") or "").strip().lower()
            if p is None:
                sem_prazo.append(n)
            elif 0 <= (p - hoje).days <= 7 and fase in FASES_PARADAS:
                risco.append((p, n, str(r.get("Orgao") or "")[:60], str(r.get("UF") or ""), str(r.get("Faixa") or ""),
                              str(r.get("Responsavel") or ""), str(r.get("Modalidade") or "")[:30]))
    risco.sort()
    grupos = {}
    for n, r in lic:
        if r.get("Trilha") in ("ARQUIVADO", "DESCARTADOS", "ENCERRADO"):
            continue
        nums = re.findall(r"\d+", str(r.get("Edital") or ""))
        cid = slug(r.get("Cidade") or "")
        nums = [x for x in nums if not re.fullmatch(r"20\d\d", x)] or nums
        if nums and cid:
            k = (cid, str(int(nums[0])), str(r.get("UF") or ""))
            grupos.setdefault(k, []).append(n)
    dup_proc = [f"{k[0]} ed.{k[1]} {k[2]}: linhas {'/'.join(map(str, v))}" for k, v in grupos.items() if len(v) > 1]
    abertos = sum(1 for _, r in lic if r.get("Trilha") in ("CREDENCIAMENTO", "PREGAO"))
    nuvem = sum(1 for _, r in lic if r.get("Origem") in ORIGENS_NUVEM and r.get("Trilha") in ("CREDENCIAMENTO", "PREGAO"))
    info["licitacoes"] = {"linhas": len(lic), "abertos": abertos, "do_radar_nuvem": nuvem,
                          "ids_repetidos": len(rep), "trilha_divergente": len(trilha_errada),
                          "score_divergente": len(score_errado), "sem_prazo": len(sem_prazo),
                          "prazo_7_dias_parados": len(risco), "processo_repetido": len(dup_proc)}
    if rep:
        alertas.append(f"{len(rep)} IDs repetidos na planilha de licitações ({', '.join(list(rep)[:5])}).")
    if len(trilha_errada) > 5:
        avisos.append(f"{len(trilha_errada)} licitações com Trilha desatualizada (a próxima sincronização corrige).")
    if score_errado:
        avisos.append(f"{len(score_errado)} licitações medidas com Score fora da régua (a próxima sincronização corrige).")
    if risco:
        alertas.append(f"{len(risco)} processos abertos vencem em até 7 dias e ainda estão parados em fase inicial: " +
                       "; ".join(f"{p.strftime('%d/%m')} {o} ({uf})" for p, _, o, uf, *_ in risco[:8]) + ".")
    if dup_proc:
        avisos.append(f"{len(dup_proc)} processos parecem estar em duas linhas (mesmo órgão e número de edital).")
    if sem_prazo:
        avisos.append(f"{len(sem_prazo)} processos abertos sem prazo na planilha.")

    status = "alerta" if alertas else ("atencao" if avisos else "ok")
    saude = {"gerado": AGORA.strftime("%Y-%m-%dT%H:%M"), "status": status,
             "alertas": alertas, "avisos": avisos, "numeros": info,
             "risco": [{"prazo": p.strftime("%d/%m/%Y"), "linha": n, "orgao": o, "uf": uf, "faixa": fx, "resp": rp, "mod": md}
                       for p, n, o, uf, fx, rp, md in risco]}
    os.makedirs("site", exist_ok=True)
    open("site/saude.js", "w", encoding="utf-8").write(
        "window.SAUDE=" + json.dumps(saude, ensure_ascii=False) + ";\n")
    for a in alertas:
        print(f"::warning title=Central TRX::{a}")
    for a in avisos:
        print(f"::notice title=Central TRX::{a}")
    # O GitHub mostra no máximo 10 avisos de cada tipo por passo: listas vão numa linha só.
    if risco:
        print("::notice title=Prazos em risco::" + " || ".join(
            f"L{n} {p.strftime('%d/%m')} {o} ({uf}) {md} {fx or 'sem faixa'} resp:{rp or 'ninguém'}"
            for p, n, o, uf, fx, rp, md in risco))
    if sem_prazo:
        print(f"::notice title=Sem prazo::linhas {', '.join(map(str, sem_prazo))}")
    if dup_proc:
        print("::notice title=Processo repetido::" + " || ".join(dup_proc))
    print("Verificação:", status, json.dumps(info, ensure_ascii=False))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(f"## Verificação da Central: {status}\n\n")
            for a in alertas: f.write(f"- ⚠️ {a}\n")
            for a in avisos: f.write(f"- {a}\n")
            f.write(f"\n```\n{json.dumps(info, ensure_ascii=False, indent=1)}\n```\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a verificação nunca derruba a publicação
        print(f"::warning title=Central TRX::A verificação falhou: {e}")
        open("site/saude.js", "w").write('window.SAUDE={"status":"erro","alertas":["A verificação automática falhou nesta rodada."],"avisos":[]};\n')
