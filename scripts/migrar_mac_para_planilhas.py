#!/usr/bin/env python3
"""Migração única (01/10/2026): leva para planilhas Google o estado que vivia em arquivos do Mac.

- quadro_data.json      -> abas "Quadro" (um município por linha) e "Quadro contatos" (um decisor por linha)
                           na planilha "Pipeline Licitações TRX"
- _ACOMPANHAMENTO_ESCLARECIMENTOS.json -> aba "Esclarecimentos" na mesma planilha
- (nova) aba "Eventos e-mail" com o cabeçalho, para o Monitor de e-mail da nuvem
- documentos_data.json + colunas da Carla do Pipeline_Documentos.xlsx -> planilha "Documentos TRX",
  abas "Documentos" e "Log"

Os arquivos de origem são cópias em _A_EXCLUIR compartilhadas só com a conta de serviço.
Roda pelo workflow migrar.yml (workflow_dispatch). Não apaga nada; só cria abas e grava valores.
Se uma aba já existe com dados, ela é regravada inteira (rodar de novo dá o mesmo resultado).
"""
import datetime as dt, io, json, os, re, unicodedata
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

LICIT_SHEET = "1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8"
DOCS_SHEET = "13nXaAsgQ4czDGnp6SZd2ConSeV_8_1exZG_lH4l9hD8"
SRC = {"quadro": "1i6xQ6xFiKlRQg-tnfpurMOJ8YOqj0pok",
       "documentos": "1QVvsx1YnuOujwgeT7g0zC6tc6U_4ZJKO",
       "xlsx": "1ibKvB61Ix10bDtPVhdRKtDUW1gnIMMEf",
       "esclarecimentos": "12Xl4ONAXWJV0snrRWonxm2yomqyVrYNP"}
TZ = dt.timezone(dt.timedelta(hours=-3))
HOJE = dt.datetime.now(TZ).strftime("%d/%m/%Y %H:%M")

cred = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SA_JSON"]),
    scopes=["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/spreadsheets"])
drive = build("drive", "v3", credentials=cred, cache_discovery=False)
sheets = build("sheets", "v4", credentials=cred, cache_discovery=False)


def baixar(fid):
    buf = io.BytesIO(); dl = MediaIoBaseDownload(buf, drive.files().get_media(fileId=fid)); done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue()


def slug(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def aba(planilha, titulo, linhas, congelar=1):
    """Cria a aba se não existir e grava as linhas a partir de A1 (limpa antes)."""
    meta = sheets.spreadsheets().get(spreadsheetId=planilha, fields="sheets.properties").execute()
    existe = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
    ncol = max(len(r) for r in linhas)
    if titulo not in existe:
        r = sheets.spreadsheets().batchUpdate(spreadsheetId=planilha, body={"requests": [{"addSheet": {"properties": {
            "title": titulo, "gridProperties": {"rowCount": len(linhas) + 200, "columnCount": max(ncol, 10),
                                                "frozenRowCount": congelar}}}}]}).execute()
        sid = r["replies"][0]["addSheet"]["properties"]["sheetId"]
    else:
        sid = existe[titulo]
        sheets.spreadsheets().values().clear(spreadsheetId=planilha, range=f"'{titulo}'").execute()
        sheets.spreadsheets().batchUpdate(spreadsheetId=planilha, body={"requests": [{"updateSheetProperties": {
            "properties": {"sheetId": sid, "gridProperties": {"rowCount": len(linhas) + 200, "columnCount": max(ncol, 10)}},
            "fields": "gridProperties(rowCount,columnCount)"}}]}).execute()
    linhas = [[("" if v is None else v) for v in r] for r in linhas]
    for i in range(0, len(linhas), 2000):
        sheets.spreadsheets().values().update(spreadsheetId=planilha, range=f"'{titulo}'!A{i + 1}",
                                              valueInputOption="RAW", body={"values": linhas[i:i + 2000]}).execute()
    sheets.spreadsheets().batchUpdate(spreadsheetId=planilha, body={"requests": [{"repeatCell": {
        "range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1},
        "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}}]}).execute()
    print(f"OK aba {titulo}: {len(linhas) - 1} linhas")
    return sid


def br(d):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(d or ""))
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else str(d or "")


# ---------- Quadro ----------
q = json.loads(baixar(SRC["quadro"]))["seeds"]
H1 = ["ID", "Municipio", "UF", "Regiao", "Gestao", "Unidades com radiologia", "TC", "RX", "MMG", "RM", "DO",
      "Prioridade", "Status", "Cred", "Proxima acao", "Nota", "Fonte", "Atualizado em"]
H2 = ["ID", "Municipio", "UF", "Nome", "Cargo", "Telefone", "WhatsApp", "E-mail", "Bounce", "Obs", "Atualizado em"]
L1, L2 = [H1], [H2]
for s in q:
    mun, uf = s.get("Município", ""), s.get("UF", "")
    qid = f"quadro-{slug(mun)}-{slug(uf)}"
    L1.append([qid, mun, uf, s.get("Região"), s.get("Gestão"), s.get("Unidades públicas com radiologia"), s.get("TC"),
               s.get("RX"), s.get("MMG"), s.get("RM"), s.get("DO"), s.get("Prioridade"), s.get("Status"), s.get("Cred"),
               s.get("Próxima ação"), s.get("Nota"), s.get("Fonte"), HOJE])
    for c in s.get("Contatos") or []:
        obs = str(c.get("obs") or "")
        b = re.search(r"\[BOUNCE[^\]]*\]", obs)
        L2.append([qid, mun, uf, c.get("nome"), c.get("cargo"), c.get("fone"), c.get("whats"), c.get("email"),
                   b.group(0) if b else "", obs, HOJE])
aba(LICIT_SHEET, "Quadro", L1)
aba(LICIT_SHEET, "Quadro contatos", L2)

# ---------- Esclarecimentos ----------
e = json.loads(baixar(SRC["esclarecimentos"]))
itens = e if isinstance(e, list) else next((v for v in e.values() if isinstance(v, list)), [])
chaves = []
for it in itens:
    for k in it:
        if k not in chaves:
            chaves.append(k)
LE = [chaves + ["Atualizado em"]] + [[json.dumps(it.get(k), ensure_ascii=False) if isinstance(it.get(k), (dict, list))
                                       else it.get(k) for k in chaves] + [HOJE] for it in itens]
if len(LE) == 1:
    LE = [["processo", "cidade", "uf", "email_destino", "enviado_em", "pergunta", "status", "detalhe", "thread_id", "Atualizado em"]]
aba(LICIT_SHEET, "Esclarecimentos", LE)

# ---------- Eventos e-mail (vazia, só cabeçalho; não regrava se já tiver linhas) ----------
meta = sheets.spreadsheets().get(spreadsheetId=LICIT_SHEET, fields="sheets.properties.title").execute()
if "Eventos e-mail" not in [s["properties"]["title"] for s in meta["sheets"]]:
    aba(LICIT_SHEET, "Eventos e-mail", [["Data", "Orgao", "Processo", "UF", "O que aconteceu", "Proximo passo",
                                         "Thread", "Status", "Registrado por"]])

# ---------- Documentos TRX ----------
sheets.spreadsheets().batchUpdate(spreadsheetId=DOCS_SHEET, body={"requests": [{"updateSpreadsheetProperties": {
    "properties": {"timeZone": "America/Sao_Paulo"}, "fields": "timeZone"}}]}).execute()
d = json.loads(baixar(SRC["documentos"]))
import openpyxl
wb = openpyxl.load_workbook(io.BytesIO(baixar(SRC["xlsx"])), data_only=True)
verdes = {}
if "DOCUMENTOS" in wb.sheetnames:
    rows = list(wb["DOCUMENTOS"].iter_rows(values_only=True))
    H = [str(h or "").strip() for h in rows[0]]
    for r in rows[1:]:
        x = dict(zip(H, r))
        if x.get("Documento"):
            verdes[str(x["Documento"]).strip()] = [x.get("Situacao"), x.get("Proxima acao"), x.get("Quando"), x.get("Notas da Carla")]
HD = ["Documento", "Nivel", "Orgao emissor", "Validade", "Dias", "Status", "Validade tipo", "Renovacao", "Responsavel",
      "Onde renovar", "Arquivo no Drive", "O que trava", "Observacao", "Conferido em",
      "Situacao", "Proxima acao", "Quando", "Notas da Carla"]
LD = [HD]
for i, x in enumerate(d["documentos"], start=2):
    dias = f'=IF(D{i}="";"";D{i}-TODAY())'
    # planilha em pt_BR: separador de argumentos é ponto e vírgula
    status = (f'=IF(D{i}="";"SEM DATA";IF(E{i}<0;"VENCIDO";IF(E{i}<=15;"VENCE EM 15 DIAS";'
              f'IF(E{i}<=30;"VENCE EM 30 DIAS";"OK"))))')
    LD.append([x.get("Documento"), x.get("Nivel"), x.get("Orgao"), br(x.get("Validade")), dias, status,
               x.get("Validade_tipo"), x.get("Renovacao"), x.get("Responsavel"), x.get("Onde_renovar"), x.get("Arquivo"),
               x.get("Bloqueia"), x.get("Observacao"), "migrado do Mac em " + HOJE]
              + (verdes.get(str(x.get("Documento")).strip()) or ["", "", "", ""]))
sid = aba(DOCS_SHEET, "Documentos", LD)
# Validade como data e fórmulas: regrava D, E e F com USER_ENTERED
sheets.spreadsheets().values().update(spreadsheetId=DOCS_SHEET, range="'Documentos'!D2",
                                      valueInputOption="USER_ENTERED",
                                      body={"values": [[r[3], r[4], r[5]] for r in LD[1:]]}).execute()
sheets.spreadsheets().batchUpdate(spreadsheetId=DOCS_SHEET, body={"requests": [{"repeatCell": {
    "range": {"sheetId": sid, "startRowIndex": 1, "startColumnIndex": 3, "endColumnIndex": 4},
    "cell": {"userEnteredFormat": {"numberFormat": {"type": "DATE", "pattern": "dd/mm/yyyy"}}},
    "fields": "userEnteredFormat.numberFormat"}}]}).execute()
LM = [["Chave", "Valor"]] + [[k, json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v]
                             for k, v in d.get("meta", {}).items()]
aba(DOCS_SHEET, "Empresa", LM)
meta = sheets.spreadsheets().get(spreadsheetId=DOCS_SHEET, fields="sheets.properties").execute()
tit = {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}
if "Log" not in tit:
    aba(DOCS_SHEET, "Log", [["Data", "Rodada", "O que mudou", "Vencidos", "Vencem em 30 dias", "Para o Marcos"],
                            [HOJE, "migração", "48 documentos migrados do documentos_data.json e colunas da Carla do Pipeline_Documentos.xlsx", "", "", ""]])
# a aba vazia que nasce com a planilha ("Página1"/"Sheet1") sai
vazias = [sid for t, sid in tit.items() if t in ("Página1", "Sheet1", "Planilha1")]
if vazias:
    sheets.spreadsheets().batchUpdate(spreadsheetId=DOCS_SHEET, body={"requests": [{"deleteSheet": {"sheetId": s}} for s in vazias]}).execute()
print("Migração concluída.")
