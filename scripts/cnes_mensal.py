#!/usr/bin/env python3
"""CNES mensal: equipamentos de imagem, serviços especializados e radiologistas do Brasil.

Baixa do FTP do DATASUS os arquivos EQ (equipamentos), SR (serviços especializados) e PF
(profissionais) da competência mais recente de cada UF, junta por CNES e grava na planilha
"CNES Imagem TRX (mensal, robô)":
- aba "CNES": uma linha por estabelecimento com algum equipamento de imagem (TC, RM,
  mamografia, RX, densitometria) ou com o serviço 121 (diagnóstico por imagem), com o número
  de radiologistas (CBO 225320) no quadro;
- aba "Municipios": uma linha por município do IBGE (todos, inclusive os sem imagem), com os
  totais do município, os radiologistas de qualquer estabelecimento dele e as linhas onde ele
  começa e termina na aba CNES. É o índice que as tarefas da Dor leem primeiro.

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
CBO_RADIOLOGISTA = "225320"   # Médico em radiologia e diagnóstico por imagem
UF_COD = {"12": "AC", "27": "AL", "13": "AM", "16": "AP", "29": "BA", "23": "CE", "53": "DF", "32": "ES",
          "52": "GO", "21": "MA", "31": "MG", "50": "MS", "51": "MT", "15": "PA", "25": "PB", "26": "PE",
          "22": "PI", "41": "PR", "33": "RJ", "24": "RN", "11": "RO", "14": "RR", "43": "RS", "42": "SC",
          "28": "SE", "35": "SP", "17": "TO"}


def ler_dbc(ftp, caminho, filtro=None):
    """Lê um .dbc do FTP. Com filtro, devolve só as linhas aceitas (o PF de SP tem milhões de linhas)."""
    import pyreaddbc, dbfread
    with tempfile.TemporaryDirectory() as d:
        dbc, dbf = os.path.join(d, "x.dbc"), os.path.join(d, "x.dbf")
        with open(dbc, "wb") as f:
            ftp.retrbinary(f"RETR {caminho}", f.write)
        pyreaddbc.dbc2dbf(dbc, dbf)
        if filtro is None:
            return [dict(r) for r in dbfread.DBF(dbf, encoding="latin-1")]
        return dbf_filtrado(dbf, *filtro)


def dbf_filtrado(caminho, campo, valor, campos):
    """Leitura rápida de DBF: compara só um campo e decodifica só os campos pedidos das linhas aceitas."""
    import struct
    with open(caminho, "rb") as f:
        cab = f.read(32)
        n, tam_cab, tam_reg = struct.unpack("<IHH", cab[4:12])
        offs, pos = {}, 1
        while True:
            d = f.read(32)
            if not d or d[0] == 0x0D:
                break
            nome = d[:11].split(b"\0")[0].decode("latin-1").strip()
            larg = d[16]
            offs[nome] = (pos, pos + larg)
            pos += larg
        f.seek(tam_cab)
        a, b = offs[campo]
        alvo = valor.encode("latin-1").ljust(b - a)
        quer = [(c, offs[c]) for c in campos if c in offs]
        out = []
        for _ in range(n):
            reg = f.read(tam_reg)
            if len(reg) < tam_reg:
                break
            if reg[0:1] == b"*" or reg[a:b] != alvo:
                continue
            out.append({c: reg[x:y].decode("latin-1").strip() for c, (x, y) in quer})
        return out


# Filtro do arquivo PF: só médicos radiologistas, com os campos que a contagem usa
FILTRO_RADIOLOGISTA = ("CBO", CBO_RADIOLOGISTA, ["CNES", "CODUFMUN", "CBO", "CNS_PROF", "CPF_PROF", "NOMEPROF", "PROF_SUS"])


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
    rad = collections.defaultdict(set)        # CNES -> profissionais radiologistas
    rad_sus = collections.defaultdict(set)    # CNES -> radiologistas que atendem SUS
    rad_mun = collections.defaultdict(set)    # município -> radiologistas em qualquer estabelecimento
    pf_ok = set()                             # UFs cujo PF foi lido (sem PF, radiologista fica em branco)
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
        pf_nome = f"PF{uf}{aamm}.dbc"
        pf = None
        # A pasta PF é grande demais para listar (o NLST estoura o tempo); baixa direto pelo nome.
        for tentativa in range(3):
            try:
                pf = ler_dbc(ftp, f"{FTP_DIR}/PF/{pf_nome}", FILTRO_RADIOLOGISTA)
                break
            except ftplib.error_perm as e:
                print(f"::warning::{uf}: PF {pf_nome} indisponível ({e})")
                break
            except Exception as e:
                print(f"::warning::{uf}: PF tentativa {tentativa + 1} falhou ({e})")
                time.sleep(10)
                ftp = ftplib.FTP(FTP_HOST, timeout=300)
                ftp.login()
        if pf is None:
            print(f"::warning::{uf}: sem arquivo PF {aamm}; radiologistas da UF ficam em branco")
        else:
            pf_ok.add(uf)
            for r in pf:
                cnes = str(r.get("CNES") or "").strip()
                quem = str(r.get("CNS_PROF") or r.get("CPF_PROF") or r.get("NOMEPROF") or "").strip() or id(r)
                rad[cnes].add(quem)
                rad_mun[str(r.get("CODUFMUN") or "")].add(quem)
                if str(r.get("PROF_SUS") or "").strip() in ("1", "S"):
                    rad_sus[cnes].add(quem)
        print(f"{uf} {comps[uf]}: EQ {len(eq)} linhas, SR {len(sr)} linhas, radiologistas no PF "
              f"{'sem arquivo' if pf is None else len(pf)}")
    ftp.quit()

    mun = municipios()
    agora = dt.datetime.now(TZ).strftime("%d/%m/%Y %H:%M")
    H = ["CNES", "CNPJ", "UF", "Codigo municipio", "Municipio", "Esfera", "Tipo unidade", "TC", "RM", "MMG", "RX",
         "DO", "US", "PET", "TC SUS", "RM SUS", "MMG SUS", "RX SUS", "Servico 121 classes", "Servicos especializados",
         "Competencia", "Atualizado em", "Radiologistas", "Radiologistas SUS"]
    linhas = []
    for e in est.values():
        img = sum(e["eq"][g] for g in ("TC", "RM", "MMG", "RX", "DO"))
        if not img and not e["s121"]:
            continue
        linhas.append([e["cnes"], e["cnpj"], e["uf"], e["mun"], mun.get(e["mun"], ""), e["esfera"], e["tp_unid"],
                       e["eq"]["TC"], e["eq"]["RM"], e["eq"]["MMG"], e["eq"]["RX"], e["eq"]["DO"], e["eq"]["US"],
                       e["eq"]["PET"], e["eq_sus"]["TC"], e["eq_sus"]["RM"], e["eq_sus"]["MMG"], e["eq_sus"]["RX"],
                       " ".join(sorted(e["s121"])), " ".join(sorted(e["serv"])), e["comp"], agora,
                       len(rad[e["cnes"]]) if e["uf"] in pf_ok else "",
                       len(rad_sus[e["cnes"]]) if e["uf"] in pf_ok else ""])
    linhas.sort(key=lambda x: (x[2], x[4], x[0]))
    print(f"Estabelecimentos com imagem: {len(linhas)} (de {len(est)} lidos)")
    if len(linhas) < 1000:
        print("::error::Poucos estabelecimentos; a planilha não foi tocada.")
        sys.exit(1)
    muni = montar_municipios(linhas, mun, rad, rad_mun, pf_ok, comps, agora)

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
           ["Radiologistas", "Profissionais distintos com CBO 225320 (médico em radiologia e diagnóstico por imagem) vinculados ao estabelecimento no arquivo PF. Em branco quando o PF da UF não foi lido; 0 quer dizer nenhum no quadro."],
           ["Radiologistas SUS", "Os mesmos, só os que atendem SUS."],
           ["Aba Municipios", "Uma linha por município do IBGE (inclusive sem imagem). Primeira e Ultima linha apontam o bloco do município na aba CNES. Radiologistas no municipio conta qualquer estabelecimento do município, com ou sem imagem."],
           ["Fonte", "FTP do DATASUS, arquivos EQ e SR por UF. Atualizado todo mês pelo GitHub (scripts/cnes_mensal.py)."]]
    if "Legenda" not in abas:
        api.batchUpdate(spreadsheetId=PLANILHA, body={"requests": [{"addSheet": {"properties": {"title": "Legenda"}}}]}).execute()
    gravar_municipios(api, abas, muni)
    api.values().update(spreadsheetId=PLANILHA, range="Legenda!A1", valueInputOption="RAW", body={"values": leg}).execute()
    print(f"CNES mensal: {len(linhas)} estabelecimentos gravados; competências {sorted(set(comps.values()))}")


def montar_municipios(linhas, mun, rad, rad_mun, pf_ok, comps, agora):
    """Uma linha por município do IBGE com o índice das linhas na aba CNES e os totais."""
    blocos = {}
    for i, l in enumerate(linhas, start=2):          # linha 1 é o cabeçalho
        b = blocos.setdefault(l[3], {"ini": i, "fim": i, "n": 0, "tc": 0, "tc_sus": 0, "rm": 0, "mmg": 0, "rx": 0,
                                     "rx_sus": 0, "us": 0, "c007": 0, "tc_sem_007": 0, "rad_img": set()})
        b["fim"], b["n"] = i, b["n"] + 1
        tc, rm, mmg, rx, us, tc_sus, rx_sus = l[7], l[8], l[9], l[10], l[12], l[14], l[17]
        tem007 = "007" in l[18].split()
        b["tc"] += tc; b["tc_sus"] += tc_sus; b["rm"] += rm; b["mmg"] += mmg; b["rx"] += rx
        b["rx_sus"] += rx_sus; b["us"] += us; b["c007"] += int(tem007)
        b["tc_sem_007"] += int(tc > 0 and not tem007)
        b["rad_img"] |= rad.get(l[0], set())
    codigos = set(mun) | set(blocos)
    H = ["UF", "Codigo municipio", "Municipio", "Estabelecimentos com imagem", "Primeira linha CNES",
         "Ultima linha CNES", "TC", "TC SUS", "RM", "MMG", "RX", "RX SUS", "US", "Unidades com 007",
         "Unidades com TC sem 007", "Radiologistas nos estab. com imagem", "Radiologistas no municipio",
         "Competencia", "Atualizado em"]
    out = []
    for c in codigos:
        uf = UF_COD.get(c[:2], "")
        b = blocos.get(c)
        radm = len(rad_mun.get(c, ())) if uf in pf_ok else ""
        if b:
            out.append([uf, c, mun.get(c, ""), b["n"], b["ini"], b["fim"], b["tc"], b["tc_sus"], b["rm"], b["mmg"],
                        b["rx"], b["rx_sus"], b["us"], b["c007"], b["tc_sem_007"],
                        len(b["rad_img"]) if uf in pf_ok else "", radm, comps.get(uf, ""), agora])
        else:
            out.append([uf, c, mun.get(c, ""), 0, "", "", 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        0 if uf in pf_ok else "", radm, comps.get(uf, ""), agora])
    out.sort(key=lambda x: (x[0], x[1]))
    print(f"Municipios: {len(out)} ({sum(1 for x in out if x[3])} com imagem)")
    return [H] + out


def gravar_municipios(api, abas, muni):
    props = {"rowCount": len(muni) + 50, "columnCount": len(muni[0]), "frozenRowCount": 1}
    if "Municipios" not in abas:
        api.batchUpdate(spreadsheetId=PLANILHA, body={"requests": [{"addSheet": {"properties": {
            "title": "Municipios", "gridProperties": props}}}]}).execute()
    else:
        api.batchUpdate(spreadsheetId=PLANILHA, body={"requests": [{"updateSheetProperties": {"properties": {
            "sheetId": abas["Municipios"]["sheetId"], "gridProperties": props},
            "fields": "gridProperties(rowCount,columnCount,frozenRowCount)"}}]}).execute()
    api.values().clear(spreadsheetId=PLANILHA, range="Municipios").execute()
    api.values().update(spreadsheetId=PLANILHA, range="Municipios!A1", valueInputOption="RAW",
                        body={"values": muni}).execute()


if __name__ == "__main__":
    main()
