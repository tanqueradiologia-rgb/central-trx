#!/usr/bin/env python3
"""Radar PNCP na nuvem: procura editais abertos de telerradiologia no PNCP e acrescenta
na planilha Google "Pipeline Licitações TRX" os que ainda não estão lá.

Substitui aos poucos o radar do Mac. Enquanto os dois rodam juntos, a chave é o ID
(numero_controle_pncp, o mesmo que o robô do Mac usa), então nada entra duplicado.
Linhas criadas aqui têm Origem "Radar PNCP (GitHub)" e o sincronizar_licitacoes.py não
as arquiva quando faltam no xlsx do Mac.

Só acrescenta linhas. Nunca altera linha que já existe.
Variável de ambiente GOOGLE_SA_JSON: chave da conta de serviço (editora da planilha).
"""
import datetime as dt, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sincronizar_licitacoes import SHEET_ID, ABA, TZ, trilha_de, col  # noqa: E402

ORIGEM = "Radar PNCP (GitHub)"
# Os 20 termos do radar do Mac (auditoria de 13/07/2026). A busca do PNCP exige TODAS as palavras
# do termo; os termos curtos (diagnostico por imagem, radiologia, mamografia...) pegam os
# credenciamentos que não escrevem "laudo". Não alongue os curtos.
TERMOS = ["telerradiologia", "telelaudo", "telediagnostico", "teleradiologia", "laudos radiologicos",
          "laudo a distancia", "emissao de laudos", "laudo de raio-x", "interpretacao de exames",
          "telemedicina laudo", "diagnostico por imagem", "exames de imagem", "radiologia",
          "servicos de radiologia", "tomografia computadorizada", "ressonancia magnetica", "mamografia",
          "densitometria", "pacs", "raio-x"]
# Filtro na mesma linha do radar do Mac: descarta ruído, mantém o "talvez".
IMAGEM = ["raio-x", "raio x", "raios x", "radiolog", "radiograf", "tomograf", "ressonanc", "mamograf",
          "densitometr", "diagnostico por imagem", "exames de imagem", "imagens radiolog"]
# Pedido de laudo remoto de imagem: entra mesmo com palavra da lista de descarte (ex.: ECG junto).
FORTE = ["telerradiolog", "laudos de exames radiolog", "laudos radiolog", "laudos de raio", "laudo de raio",
         "laudos de tomograf", "laudos de imagens"]
REMOTO = ["telemedicina", "a distancia", "remot", "telelaudo", "pacs"]
FORA = ["equipament", "mamografo", "aparelho de raio", "aquisicao", "compra de", "insumo", "filme radiograf",
        "filme radiolog", "konica", "manutencao", "calibracao", "dosimetr", "contraste", "gadolin",
        "marcacao pre-cirurgica", "protecao radiologica", "odontolog", "veterinar", "eletrocardiograma",
        "ecg", "holter", "eletroencefalo", "analises clinicas", "esteriliza", "medicina do trabalho",
        "hospedagem", "hotel", "obra", "reforma", "engenharia", "pavimenta", "uniforme", "combustivel",
        "colchao", "medicamento", "veicular", "vistoria", "unidade movel", "itinerante"]
# Encaixe: alta = laudo remoto de imagem; baixa = trabalho presencial ou preço abaixo do piso.
PRESENCIAL = ["plantoes", "plantao", "por quilometro", "r$/km", "deslocamento", "biopsia", "ultrassonografia",
              "ultrassom", "usg", "doppler", "carga horaria", "tecnico em radiologia", "tecnicos em radiologia",
              "operador de raio", "realizacao de exames", "com equipamento proprio", "consultorio movel",
              "veiculo movel"]
# Piso de venda por laudo (nunca abaixo). RX: decisão do Marcos em 01/10/2026 (R$ 10,00).
# TC, RM e MMG: repasse ao radiologista dividido por 0,81 (19% de impostos e comissões).
PISOS = [("RX", ["raio-x", "raio x", "raios x", "radiograf", " rx "], 10.00),
         ("MMG", ["mamograf"], 22.22),
         ("TC", ["tomograf"], 43.21),
         ("RM", ["ressonanc"], 61.73)]
DESCARTE_FASE = "Descartado"
DESCARTE_MOTIVO = "Ruído do radar PNCP da nuvem (fora do filtro de telelaudo)"
URL = "https://pncp.gov.br/api/search/"


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()


def buscar(termo):
    itens, pagina = [], 1
    while pagina <= 2:
        q = urllib.parse.urlencode({"tipos_documento": "edital", "status": "recebendo_proposta",
                                    "q": termo, "tam_pagina": 100, "pagina": pagina,
                                    "ordenacao": "-data"})
        req = urllib.request.Request(f"{URL}?{q}", headers={"User-Agent": "central-trx/1.0",
                                                           "Accept": "application/json"})
        doc = None
        for tentativa in range(4):  # o PNCP às vezes derruba a conexão; tenta de novo com espera
            try:
                with urllib.request.urlopen(req, timeout=40) as r:
                    doc = json.load(r)
                break
            except Exception:
                if tentativa == 3:
                    raise
                time.sleep(5 * (tentativa + 1) ** 2)
        lote = doc.get("items") or []
        itens += lote
        if len(lote) < 100:
            break
        pagina += 1
        time.sleep(1)
    return itens


def data_br(v):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(v or ""))
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else ""


def linha_de(it, agora):
    cnpj = str(it.get("orgao_cnpj") or "")
    ano, seq = it.get("ano"), it.get("numero_sequencial")
    link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if cnpj and ano and seq else ""
    item_url = str(it.get("item_url") or "")
    if item_url and not link:
        link = "https://pncp.gov.br/app" + item_url.replace("/compras/", "/editais/")
    valor = it.get("valor_global")
    return {
        "ID": str(it.get("numero_controle_pncp") or "").strip(),
        "Fase": "Mapeado",
        "Responsavel": "Carla",  # mesmo padrão do robô do Mac
        "Orgao": it.get("orgao_nome") or "",
        "Cidade": it.get("municipio_nome") or "",
        "UF": it.get("uf") or "",
        "Modalidade": it.get("modalidade_licitacao_nome") or "",
        "Edital": it.get("title") or "",
        "Objeto": (it.get("description") or "")[:1000],
        "Valor estimado": valor if isinstance(valor, (int, float)) and valor > 0 else "",
        "Prazo": data_br(it.get("data_fim_vigencia")),
        "Link PNCP": link,
        "Origem": ORIGEM,
        "Atualizado em": agora,
        "Sincronizado em": agora,
    }


def relevante(it):
    txt = sem_acento(f"{it.get('title', '')} {it.get('description', '')}")
    img = any(k in txt for k in IMAGEM)
    if any(k in txt for k in FORTE) or (img and any(k in txt for k in REMOTO)):
        return True
    return img and not any(k in txt for k in FORA)


def encaixe_texto(it):
    """Encaixe só pelo texto do edital: alta, media ou baixa (com motivo).
    Laudo remoto de imagem = alta; laudo remoto junto com parte presencial = media;
    só presencial (realização de exames, ultrassom, plantão) = baixa."""
    txt = " " + sem_acento(f"{it.get('title', '')} {it.get('description', '')}") + " "
    pres = [k for k in PRESENCIAL if k in txt]
    img = any(k in txt for k in IMAGEM)
    remoto = any(k in txt for k in FORTE) or (img and any(k in txt for k in REMOTO))
    if remoto and not pres:
        return "alta", ""
    if remoto:
        return "media", "laudo remoto com parte presencial: " + ", ".join(pres[:3])
    if pres:
        return "baixa", "presencial ou fora do telelaudo: " + ", ".join(pres[:3])
    return "media", ""


def checar_piso(cnpj, ano, seq):
    """Lê os itens do PNCP e devolve a lista de itens com valor unitário abaixo do piso."""
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens?pagina=1&tamanhoPagina=200"
    req = urllib.request.Request(url, headers={"User-Agent": "central-trx/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        itens = json.load(r)
    abaixo = []
    for i in itens if isinstance(itens, list) else []:
        desc = " " + sem_acento(i.get("descricao") or "") + " "
        vu = i.get("valorUnitarioEstimado")
        if not isinstance(vu, (int, float)) or vu < 1:  # R$ 0,01 é valor simbólico, não preço
            continue
        for nome, chaves, piso in PISOS:
            if any(k in desc for k in chaves) and vu < piso:
                abaixo.append(f"{nome} R$ {vu:.2f} (piso R$ {piso:.2f})".replace(".", ","))
                break
    return abaixo


def avaliar(it):
    """Encaixe e bloqueio de um edital novo: texto mais o teste de preço pelos itens do PNCP."""
    enc, motivo = encaixe_texto(it)
    m = re.match(r"^(\d{14})-1-0*(\d+)/(\d{4})$", str(it.get("numero_controle_pncp") or "").strip())
    if m:
        try:
            abaixo = checar_piso(m.group(1), m.group(3), m.group(2))
            if abaixo:
                enc = "baixa"
                motivo = (motivo + "; " if motivo else "") + "preço abaixo do piso: " + "; ".join(abaixo[:3])
            time.sleep(1)
        except Exception as e:
            print(f"  itens sem resposta para {it.get('numero_controle_pncp')}: {e}")
    return enc, motivo


def limpar_ruido(api, H, ix, agora):
    """Linhas que este radar criou e que o filtro atual rejeita saem da fila (Fase Descartado).
    Só mexe em linha com Origem deste radar e Fase ainda Mapeado."""
    vals = api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!A1:{col(len(H))}").execute().get("values", [])
    mud = []
    for n, r in enumerate(vals[1:], start=2):
        r = r + [""] * (len(H) - len(r))
        if r[ix["Origem"]] != ORIGEM or r[ix["Fase"]].strip().lower() != "mapeado":
            continue
        if relevante({"title": r[ix["Edital"]], "description": r[ix["Objeto"]]}):
            if "Responsavel" in ix and not str(r[ix["Responsavel"]]).strip():
                mud.append({"range": f"{ABA}!{col(ix['Responsavel'] + 1)}{n}", "values": [["Carla"]]})
            bloq = str(r[ix["Bloqueio"]]).strip() if "Bloqueio" in ix else ""
            auto = bloq.startswith("presencial ou fora") or bloq.startswith("laudo remoto com parte")
            if "Encaixe" in ix and (not str(r[ix["Encaixe"]]).strip() or auto):  # encaixe pelo texto
                enc, motivo = encaixe_texto({"title": r[ix["Edital"]], "description": r[ix["Objeto"]]})
                if enc != str(r[ix["Encaixe"]]).strip():
                    mud.append({"range": f"{ABA}!{col(ix['Encaixe'] + 1)}{n}", "values": [[enc]]})
                if "Bloqueio" in ix and (not bloq or auto) and motivo != bloq:
                    mud.append({"range": f"{ABA}!{col(ix['Bloqueio'] + 1)}{n}", "values": [[motivo]]})
            continue
        mud += [{"range": f"{ABA}!{col(ix['Fase'] + 1)}{n}", "values": [[DESCARTE_FASE]]},
                {"range": f"{ABA}!{col(ix['Resultado'] + 1)}{n}", "values": [[DESCARTE_MOTIVO]]},
                {"range": f"{ABA}!{col(ix['Trilha'] + 1)}{n}", "values": [["DESCARTADOS"]]},
                {"range": f"{ABA}!{col(ix['Sincronizado em'] + 1)}{n}", "values": [[agora]]}]
    if mud:
        api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": mud}).execute()
    return sum(1 for m in mud if m["values"] == [[DESCARTE_FASE]])


def completar_prazos(api, H, ix, agora, limite=30):
    """Processo aberto sem prazo e com ID no formato do PNCP ({cnpj}-1-{seq}/{ano}): busca a data
    de encerramento das propostas na API de consulta do PNCP e grava só a coluna Prazo."""
    if "Prazo" not in ix:
        return 0
    vals = api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!A1:{col(len(H))}").execute().get("values", [])
    mud, feitas = [], 0
    for n, r in enumerate(vals[1:], start=2):
        if feitas >= limite:
            break
        r = r + [""] * (len(H) - len(r))
        if r[ix["Trilha"]] not in ("CREDENCIAMENTO", "PREGAO") or str(r[ix["Prazo"]]).strip():
            continue
        m = re.match(r"^(\d{14})-1-0*(\d+)/(\d{4})$", str(r[ix["ID"]]).strip())
        if not m:
            continue
        cnpj, seq, ano = m.groups()
        url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "central-trx/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                doc = json.load(resp)
        except Exception as e:
            print(f"  prazo: linha {n} sem resposta do PNCP ({e})")
            continue
        fim = str(doc.get("dataEncerramentoProposta") or "")
        mm = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?", fim)
        if not mm:
            continue
        y, mo, d, hh, mi = mm.groups()
        valor = f"{d}/{mo}/{y}" + (f" {hh}:{mi}" if hh else "")
        mud += [{"range": f"{ABA}!{col(ix['Prazo'] + 1)}{n}", "values": [[valor]]},
                {"range": f"{ABA}!{col(ix['Sincronizado em'] + 1)}{n}", "values": [[agora]]}]
        feitas += 1
        print(f"  prazo: linha {n} {r[ix['Orgao']][:40]} -> {valor}")
        time.sleep(1)
    if mud:
        api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": mud}).execute()
    return feitas


def main():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    api = build("sheets", "v4", credentials=cred, cache_discovery=False).spreadsheets()
    H = [str(h).strip() for h in api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!1:1")
         .execute().get("values", [[]])[0]]
    ix = {h: i for i, h in enumerate(H)}
    agora = dt.datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    limpas = limpar_ruido(api, H, ix, agora)  # não depende do PNCP responder
    try:
        prazos = completar_prazos(api, H, ix, agora)
    except Exception as e:
        prazos = 0
        print(f"::warning::Completar prazos falhou: {e}")

    achados, erros = {}, 0
    from concurrent.futures import ThreadPoolExecutor
    # O PNCP derruba conexões quando recebe muitas buscas juntas. Cada rodada faz os 4 termos de
    # telelaudo e metade dos outros (alternando pela hora): todo termo é buscado ao menos a cada 2 h.
    fixos, resto = TERMOS[:4], TERMOS[4:]
    hora = dt.datetime.now(TZ).hour
    termos = fixos + [t for i, t in enumerate(resto) if i % 2 == hora % 2]
    with ThreadPoolExecutor(max_workers=2) as ex:
        futuros = {t: ex.submit(buscar, t) for t in termos}
    for t, f in futuros.items():
        try:
            for it in f.result():
                rid = str(it.get("numero_controle_pncp") or "").strip()
                if rid and relevante(it):
                    achados[rid] = it
        except Exception as e:  # um termo com erro não derruba os outros
            erros += 1
            print(f"::warning::PNCP falhou para '{t}': {e}")
    if erros == len(termos):
        print(f"Radar PNCP: {limpas} linhas de ruído descartadas; PNCP não respondeu a nenhum termo.")
        sys.exit(1)

    ids = api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!{col(ix['ID'] + 1)}2:{col(ix['ID'] + 1)}") \
        .execute().get("values", [])
    existentes = {str(r[0]).strip() for r in ids if r}
    novas = []
    for rid, it in achados.items():
        if rid in existentes:
            continue
        reg = linha_de(it, agora)
        reg["Trilha"] = trilha_de(reg)
        if reg["Trilha"] == "ENCERRADO":
            continue
        reg["Encaixe"], reg["Bloqueio"] = avaliar(it)
        novas.append([reg.get(h, "") for h in H])
        print("  novo:", rid, "|", reg["Orgao"], "|", reg["Cidade"], reg["UF"], "|", reg["Prazo"], "|", reg["Encaixe"])
    if novas:
        api.values().append(spreadsheetId=SHEET_ID, range=f"{ABA}!A1", valueInputOption="RAW",
                            insertDataOption="INSERT_ROWS", body={"values": novas}).execute()
    print(f"Radar PNCP: {len(achados)} editais relevantes abertos, {len(novas)} novos na planilha, "
          f"{limpas} linhas de ruído descartadas, {prazos} prazos completados, {len(termos)} termos, {erros} com erro.")


if __name__ == "__main__":
    main()
