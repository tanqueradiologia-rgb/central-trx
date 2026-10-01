#!/usr/bin/env python3
"""CNES mensal: equipamentos de imagem e serviços especializados de cada estabelecimento do Brasil.

Baixa do FTP do DATASUS os arquivos EQ (equipamentos) e SR (serviços especializados) da
competência mais recente de cada UF, junta por CNES e grava a aba "CNES" da planilha
"CNES Imagem TRX (mensal, robô)". Entram só os estabelecimentos com algum equipamento de
imagem (TC, RM, mamografia, RX, densitometria) ou com o serviço 121 (diagnóstico por imagem).

As tarefas que medem a Dor (clínicas particulares e órgãos públicos) leem esta aba em vez do
CnesWeb, que vive fora do ar. Chave de cruzamento: CNPJ (só dígitos) ou CNES.

Variável de ambiente GOOGLE_SA_JSON: chave da conta de serviço (editora da planilha).
"""
import collections, datetime as dt, ftplib, io, json, os, sys, tempfile, time, urllib.request

PLANILHA = "1ixiAadg8BfSBhv-HjhdGaWnpxaC0XIL3YMG4qWj_xyM"
FTP_HOST, FTP_DIR = "ftp.datasus.gov.br", "/dissemin/publicos/CNES/200508_/Dados"
UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE",
       "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
# Tipo 1 do CNES (equipamentos de diagnóstico por imagem): código -> grupo
GRUPO = {2: "MMG", 3: "MMG", 17: "MMG", 4: "RX", 5: "RX", 6: "RX", 8: "RX", 9: "DO", 11: "TC", 12: "RM",
         13: "US", 14: "US", 15: "US", 18: "PET"}
ESFERA = {"M": "Municipal", "E": "Estadual", "F": "Federal", "P": "Privada"}
NATUREZA = {"1": "Pública", "2": "Privada", "3": "Sem fins lucrativos", "4": "Pessoa física"}


def esfera_de(r):
    """Esfera administrativa; quando o CNES deixa em branco (comum nas privadas), usa a natureza jurídica."""
    e = ESFERA.get(str(r.get("ESFERA_A") or "").strip(), "")
    return e or NATUREZA.get(str(r.get("NAT_JUR") or "").strip()[:1], "")
TZ = dt.timezone(dt.timedelta(hours=-3))


def ler_dbc(ftp, caminho):
    import pyreaddbc, dbfread
    with tempfile.TemporaryDirectory() as d:
        dbc, dbf = os.path.join(d, "x.dbc"), os.path.join(d, "x.dbf")
        with open(dbc, "wb") as f:
            ftp.retrbinary(f"RETR {caminho}", f.write)
        pyreaddbc.dbc2dbf(dbc, dbf)
        return [dict(r) for r in dbfread.DBF(dbf, encoding="latin-1")]


def municipios():
    try:
        req = urllib.request.Request("https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
                                     headers={"Accept-Encoding": "gzip"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        if raw[:2] == b"\x1f\x8b":
            import gzip
            raw = gzip.decompress(raw)
        return {str(m["id"])[:6]: m["nome"] for m in json.loads(raw)}
    except Exception as e:
        print(f"::warning::IBGE sem resposta ({e}); municípios ficam só com o código")
        return {}


def main():
    ftp = ftplib.FTP(FTP_HOST, timeout=120)
    ftp.login()
    lista = {t: set(ftp.nlst(f"{FTP_DIR}/{t}")) for t in ("EQ", "SR")}
    nomes = {t: {os.path.basename(p) for p in v} for t, v in lista.items()}
    est = {}
    comps = {}
    for uf in UFS:
        cands = sorted(n for n in nomes["EQ"] if n.startswith(f"EQ{uf}") and n.endswith(".dbc"))
        if not cands:
            print(f"::warning::{uf}: sem arquivo EQ")
            continue
        arq = cands[-1]
        aamm = arq[4:8]
        comps[uf] = f"20{aamm[:2]}-{aamm[2:]}"
        for tentativa in range(3):
            try:
                eq = ler_dbc(ftp, f"{FTP_DIR}/EQ/{arq}")
                sr_nome = f"SR{uf}{aamm}.dbc"
                sr = ler_dbc(ftp, f"{FTP_DIR}/SR/{sr_nome}") if sr_nome in nomes["SR"] else []
                break
            except Exception as e:
                print(f"::warning::{uf}: tentativa {tentativa + 1} falhou ({e})")
                time.sleep(10)
                ftp = ftplib.FTP(FTP_HOST, timeout=120)
                ftp.login()
        else:
            continue
        for r in eq:
            cnes = str(r.get("CNES") or "").strip()
            e = est.setdefault(cnes, {"cnes": cnes, "uf": uf, "mun": str(r.get("CODUFMUN") or ""),
                                      "cnpj": "", "esfera": esfera_de(r),
                                      "tp_unid": str(r.get("TP_UNID") or ""), "eq": collections.Counter(),
                                      "eq_sus": collections.Counter(), "s121": set(), "serv": set(), "comp": comps[uf]})
            if str(r.get("PF_PJ") or "") == "3" and not e["cnpj"]:
                e["cnpj"] = str(r.get("CPF_CNPJ") or "").strip()
            try:
                tipo, cod = int(str(r.get("TIPEQUIP") or "0")), int(str(r.get("CODEQUIP") or "0"))
            except ValueError:
                continue
            if tipo == 1 and cod in GRUPO:
                q = int(r.get("QT_EXIST") or 0)
                e["eq"][GRUPO[cod]] += q
                if str(r.get("IND_SUS") or "") == "1":
                    e["eq_sus"][GRUPO[cod]] += q
        for r in sr:
            cnes = str(r.get("CNES") or "").strip()
            serv, cls = str(r.get("SERV_ESP") or "").strip(), str(r.get("CLASS_SR") or "").strip()
            e = est.get(cnes)
            if e is None:
                e = est.setdefault(cnes, {"cnes": cnes, "uf": uf, "mun": str(r.get("CODUFMUN") or ""),
                                          "cnpj": str(r.get("CPF_CNPJ") or "").strip() if str(r.get("PF_PJ") or "") == "3" else "",
                                          "esfera": esfera_de(r),
                                          "tp_unid": str(r.get("TP_UNID") or ""), "eq": collections.Counter(),
                                          "eq_sus": collections.Counter(), "s121": set(), "serv": set(), "comp": comps[uf]})
            if serv:
                e["serv"].add(serv)
            if serv == "121" and cls:
                e["s121"].add(cls)
        print(f"{uf} {comps[uf]}: EQ {len(eq)} linhas, SR {len(sr)} linhas")
    ftp.quit()

    mun = municipios()
    agora = dt.datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    H = ["CNES", "CNPJ", "UF", "Codigo municipio", "Municipio", "Esfera", "Tipo unidade", "TC", "RM", "MMG", "RX",
         "DO", "US", "PET", "TC SUS", "RM SUS", "MMG SUS", "RX SUS", "Servico 121 classes", "Servicos especializados",
         "Competencia", "Atualizado em"]
    linhas = []
    for e in est.values():
        img = sum(e["eq"][g] for g in ("TC", "RM", "MMG", "RX", "DO"))
        if not img and not e["s121"]:
            continue
        linhas.append([e["cnes"], e["cnpj"], e["uf"], e["mun"], mun.get(e["mun"], ""), e["esfera"], e["tp_unid"],
                       e["eq"]["TC"], e["eq"]["RM"], e["eq"]["MMG"], e["eq"]["RX"], e["eq"]["DO"], e["eq"]["US"],
                       e["eq"]["PET"], e["eq_sus"]["TC"], e["eq_sus"]["RM"], e["eq_sus"]["MMG"], e["eq_sus"]["RX"],
                       " ".join(sorted(e["s121"])), " ".join(sorted(e["serv"])), e["comp"], agora])
    linhas.sort(key=lambda x: (x[2], x[4], x[0]))
    print(f"Estabelecimentos com imagem: {len(linhas)} (de {len(est)} lidos)")
    if len(linhas) < 1000:
        print("::error::Poucos estabelecimentos; a planilha não foi tocada.")
        sys.exit(1)

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    cred = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SA_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    api = build("sheets", "v4", credentials=cred, cache_discovery=False).spreadsheets()
    meta = api.get(spreadsheetId=PLANILHA, fields="sheets.properties").execute()
    abas = {s["properties"]["title"]: s["properties"] for s in meta["sheets"]}
    req = []
    if "CNES" not in abas:
        req.append({"addSheet": {"properties": {"title": "CNES", "gridProperties": {
            "rowCount": len(linhas) + 100, "columnCount": len(H), "frozenRowCount": 1}}}})
    else:
        req.append({"updateSheetProperties": {"properties": {"sheetId": abas["CNES"]["sheetId"], "gridProperties": {
            "rowCount": len(linhas) + 100, "columnCount": len(H), "frozenRowCount": 1}},
            "fields": "gridProperties(rowCount,columnCount,frozenRowCount)"}})
    api.batchUpdate(spreadsheetId=PLANILHA, body={"requests": req}).execute()
    api.values().clear(spreadsheetId=PLANILHA, range="CNES").execute()
    tudo = [H] + linhas
    for i in range(0, len(tudo), 8000):
        bloco = tudo[i:i + 8000]
        api.values().update(spreadsheetId=PLANILHA, range=f"CNES!A{i + 1}", valueInputOption="RAW",
                            body={"values": bloco}).execute()
        time.sleep(2)
    leg = [["Coluna", "O que é"],
           ["TC, RM, MMG, RX, DO, US, PET", "Quantidade de aparelhos existentes (tipo 1 do CNES). MMG soma mamógrafo simples, estereotaxia e computadorizado; RX soma até 100 mA, 100 a 500 mA, mais de 500 mA e fluoroscopia."],
           ["... SUS", "Quantidade marcada como disponível ao SUS."],
           ["Servico 121 classes", "Classificações do serviço especializado 121 (diagnóstico por imagem) declaradas pelo estabelecimento."],
           ["Servicos especializados", "Todos os códigos de serviço especializado do estabelecimento."],
           ["Competencia", "Mês do arquivo do DATASUS usado para a UF."],
           ["Fonte", "FTP do DATASUS, arquivos EQ e SR por UF. Atualizado todo mês pelo GitHub (scripts/cnes_mensal.py)."]]
    if "Legenda" not in abas:
        api.batchUpdate(spreadsheetId=PLANILHA, body={"requests": [{"addSheet": {"properties": {"title": "Legenda"}}}]}).execute()
    api.values().update(spreadsheetId=PLANILHA, range="Legenda!A1", valueInputOption="RAW", body={"values": leg}).execute()
    print(f"CNES mensal: {len(linhas)} estabelecimentos gravados; competências {sorted(set(comps.values()))}")


if __name__ == "__main__":
    main()
