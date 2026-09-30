#!/usr/bin/env python3
"""Baixa as planilhas-fonte da Central TRX com uma conta de serviço do Google (só leitura).

Variável de ambiente GOOGLE_SA_JSON: conteúdo do arquivo JSON da chave da conta de serviço.
Gera: pipeline.json, Pipeline_Licitacoes.xlsx e mods.env (datas de modificação em Brasília).
"""
import datetime as dt, io, json, os, sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

PIPELINE_ID = "1rdhgZ_ps8Ih-wwj1dF4WuQhVsz_CnCLJI8JJwTyK9u0"
LICIT_ID = "1FTHl-0FePl8aSIwGEuzFAj-P1GWEx_H1"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly",
          "https://www.googleapis.com/auth/spreadsheets.readonly"]

info = json.loads(os.environ["GOOGLE_SA_JSON"])
cred = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
drive = build("drive", "v3", credentials=cred, cache_discovery=False)
sheets = build("sheets", "v4", credentials=cred, cache_discovery=False)

vals = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Pipeline!A1:AO").execute()
json.dump(vals, open("pipeline.json", "w", encoding="utf-8"), ensure_ascii=False)

req = drive.files().get_media(fileId=LICIT_ID)
buf = io.BytesIO(); dl = MediaIoBaseDownload(buf, req); done = False
while not done:
    _, done = dl.next_chunk()
open("Pipeline_Licitacoes.xlsx", "wb").write(buf.getvalue())

def mod(fid):
    t = drive.files().get(fileId=fid, fields="modifiedTime").execute()["modifiedTime"]
    d = dt.datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(dt.timezone(dt.timedelta(hours=-3)))
    return d.strftime("%Y-%m-%dT%H:%M")

open("mods.env", "w").write(f"MOD_PIPELINE={mod(PIPELINE_ID)}\nMOD_LICIT={mod(LICIT_ID)}\n")
print(f"OK: pipeline {len(vals.get('values', []))} linhas, xlsx {len(buf.getvalue())//1024} KB")
