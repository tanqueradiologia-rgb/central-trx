#!/usr/bin/env python3
"""Aplica na planilha Google de licitações as medições da Dor guardadas em medicoes/*.json.

Cada arquivo: {"data": "AAAA-MM-DD", "medicoes": {ID: {"Eixo Necessidade": 10, "Eixo Dor": 10, ...}}}
Regra: a medição do arquivo só entra quando a linha não tem "Medido em" ou tem uma data
mais antiga que a do arquivo. Assim uma medição feita depois, direto na planilha (pela
tarefa na nuvem ou à mão), nunca é atropelada por um arquivo velho.
O Score e a Faixa são calculados depois pelo sincronizar_licitacoes.py.
"""
import datetime as dt, glob, json, os, re, sys

SHEET_ID = "1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8"
ABA = "Licitacoes"
AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(os.path.dirname(AQUI), "medicoes")


def col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def data_de(v):
    s = str(v or "").strip()
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


def main():
    arquivos = sorted(glob.glob(os.path.join(PASTA, "*.json")))
    if not arquivos:
        print("Medições: nenhum arquivo.")
        return
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    api = build("sheets", "v4", credentials=cred, cache_discovery=False).spreadsheets()
    vals = api.values().get(spreadsheetId=SHEET_ID, range=f"{ABA}!A1:AZ",
                            valueRenderOption="FORMATTED_VALUE").execute().get("values", [])
    H = [str(h).strip() for h in vals[0]]
    ix = {h: i for i, h in enumerate(H) if h}
    if "Medido em" not in ix:
        sys.exit("ERRO: a planilha não tem a coluna 'Medido em'.")
    linha_de = {}
    for n, r in enumerate(vals[1:], start=2):
        r = r + [""] * (len(H) - len(r))
        if r[ix["ID"]]:
            linha_de[str(r[ix["ID"]]).strip()] = (n, r)
    mud, aplicadas = [], 0
    for arq in arquivos:
        doc = json.load(open(arq, encoding="utf-8"))
        d_arq = data_de(doc.get("data"))
        for rid, campos in doc.get("medicoes", {}).items():
            if rid not in linha_de:
                continue
            n, r = linha_de[rid]
            d_lin = data_de(r[ix["Medido em"]])
            if d_lin and d_arq and d_lin >= d_arq:
                continue
            for c, v in campos.items():
                if c in ix and str(r[ix[c]]) != str(v):
                    mud.append({"range": f"{ABA}!{col(ix[c] + 1)}{n}", "values": [[v]]})
                    r[ix[c]] = v
            if d_arq:
                r[ix["Medido em"]] = d_arq.strftime("%d/%m/%Y")
            aplicadas += 1
    for i in range(0, len(mud), 500):
        api.values().batchUpdate(spreadsheetId=SHEET_ID, body={"valueInputOption": "RAW", "data": mud[i:i + 500]}).execute()
    print(f"Medições: {aplicadas} linhas aplicadas, {len(mud)} células, {len(arquivos)} arquivo(s).")


if __name__ == "__main__":
    main()
