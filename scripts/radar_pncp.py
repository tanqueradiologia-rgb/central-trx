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
TERMOS = ["telerradiologia", "telelaudo", "laudo a distância", "laudos radiológicos",
          "laudos de exames de imagem", "telemedicina radiologia"]
# O objeto precisa falar de laudo/imagem para entrar.
EXIGE = ["telerradiolog", "telelaudo", "laudo", "radiolog", "diagnostico por imagem",
         "tomografia", "ressonancia", "mamografia", "raio x", "raio-x", "telemedicina"]
# Compra de aparelho ou obra não interessa.
FORA = ["aquisicao de equipamento", "aquisicao de aparelho", "manutencao preventiva",
        "manutencao corretiva", "locacao de equipamento", "obra", "reforma", "filme radiologico",
        "pelicula", "dosimetria", "protecao radiologica"]
URL = "https://pncp.gov.br/api/search/"


def sem_acento(t):
    return unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()


def buscar(termo):
    itens, pagina = [], 1
    while pagina <= 5:
        q = urllib.parse.urlencode({"tipos_documento": "edital", "status": "recebendo_proposta",
                                    "q": termo, "tam_pagina": 100, "pagina": pagina,
                                    "ordenacao": "-data"})
        req = urllib.request.Request(f"{URL}?{q}", headers={"User-Agent": "central-trx/1.0",
                                                           "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=40) as r:
            doc = json.load(r)
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
    return any(k in txt for k in EXIGE) and not any(k in txt for k in FORA)


def main():
    achados, erros = {}, 0
    for t in TERMOS:
        try:
            for it in buscar(t):
                rid = str(it.get("numero_controle_pncp") or "").strip()
                if rid and relevante(it):
                    achados[rid] = it
        except Exception as e:  # um termo com erro não derruba os outros
            erros += 1
            print(f"::warning::PNCP falhou para '{t}': {e}")
        time.sleep(1)
    if erros == len(TERMOS):
        sys.exit("ERRO: o PNCP não respondeu a nenhum termo.")

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    api = build("sheets", "v4", credentials=cred, cache_discovery=False).spreadsheets()
    H = [str(h).strip() for h in api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!1:1")
         .execute().get("values", [[]])[0]]
    ix = {h: i for i, h in enumerate(H)}
    ids = api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!{col(ix['ID'] + 1)}2:{col(ix['ID'] + 1)}") \
        .execute().get("values", [])
    existentes = {str(r[0]).strip() for r in ids if r}

    agora = dt.datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    novas = []
    for rid, it in achados.items():
        if rid in existentes:
            continue
        reg = linha_de(it, agora)
        reg["Trilha"] = trilha_de(reg)
        if reg["Trilha"] == "ENCERRADO":
            continue
        novas.append([reg.get(h, "") for h in H])
        print("  novo:", rid, "|", reg["Orgao"], "|", reg["Cidade"], reg["UF"], "|", reg["Prazo"])
    if novas:
        api.values().append(spreadsheetId=SHEET_ID, range=f"{ABA}!A1", valueInputOption="RAW",
                            insertDataOption="INSERT_ROWS", body={"values": novas}).execute()
    print(f"Radar PNCP: {len(achados)} editais relevantes abertos, {len(novas)} novos na planilha, "
          f"{erros} termo(s) com erro.")


if __name__ == "__main__":
    main()
