#!/usr/bin/env python3
"""Baixa as planilhas-fonte da Central TRX com uma conta de serviço do Google (só leitura).

Variável de ambiente GOOGLE_SA_JSON: conteúdo do arquivo JSON da chave da conta de serviço.
Gera: pipeline.json e mods.env (datas de modificação em Brasília).
Com --so-licitacoes: gera só licitacoes.json (aba Licitacoes da planilha Google), depois
da sincronização, e acrescenta MOD_LICIT_SHEET ao mods.env.
"""
import datetime as dt, io, json, os, sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

PIPELINE_ID = "1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0"
LICIT_ID = "1FTHl-0FePl8aSIwGEuzFAj-P1GWEx_H1"          # xlsx que o robô do Mac grava
LICIT_SHEET = "1ReCnYKNThynTD6-xxvyuDKQ33pakPrZBDqg_1U0PPe8"  # planilha Google da equipe
SCOPES = ["https://www.googleapis.com/auth/drive.readonly",
          "https://www.googleapis.com/auth/spreadsheets.readonly"]

info = json.loads(os.environ["GOOGLE_SA_JSON"])
cred = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
drive = build("drive", "v3", credentials=cred, cache_discovery=False)
sheets = build("sheets", "v4", credentials=cred, cache_discovery=False)

def mod(fid):
    t = drive.files().get(fileId=fid, fields="modifiedTime").execute()["modifiedTime"]
    d = dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(dt.timezone(dt.timedelta(hours=-3)))
    return d.strftime("%Y-%m-%dT%H:%M")

if "--so-licitacoes" in sys.argv:
    lv = sheets.spreadsheets().values().get(spreadsheetId=LICIT_SHEET, range="Licitacoes!A1:AZ").execute()
    json.dump(lv, open("licitacoes.json", "w", encoding="utf-8"), ensure_ascii=False)
    open("mods.env", "a").write(f"MOD_LICIT_SHEET={mod(LICIT_SHEET)}\n")
    print(f"OK: licitacoes {len(lv.get('values', []))} linhas")
    sys.exit(0)

vals = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Pipeline!A1:AO").execute()
json.dump(vals, open("pipeline.json", "w", encoding="utf-8"), ensure_ascii=False)

# O xlsx do robô do Mac (LICIT_ID) deixou de ser baixado em 02/10/2026: o radar do Mac foi
# aposentado e a planilha Google de licitações é a única fonte.
open("mods.env", "w").write(f"MOD_PIPELINE={mod(PIPELINE_ID)}\n")
print(f"OK: pipeline {len(vals.get('values', []))} linhas")
