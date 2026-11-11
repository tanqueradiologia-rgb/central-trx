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
DOCS_SHEET = "13nXaAsgQ4czDGnp6SZd2ConSeV_8_1exZG_lH4l9hD8"   # Documentos TRX (fonte da verdade)
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
    # Documentos TRX: so para o aviso de vencidos e desatualizados. Falha aqui nao derruba a pagina.
    try:
        dv = sheets.spreadsheets().values().get(spreadsheetId=DOCS_SHEET, range="Documentos!A1:T").execute()
        json.dump(dv, open("documentos.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: documentos {len(dv.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("documentos.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler a planilha Documentos TRX: {e}")
    # Destaque ISGH (prioridade maxima definida pelo Marcos em 08/11/2026): aba Destaque_ISGH da
    # Pipeline Licitacoes. Falha aqui nao derruba a pagina; sem a aba, a faixa simplesmente nao aparece.
    try:
        gv = sheets.spreadsheets().values().get(spreadsheetId=LICIT_SHEET, range="Destaque_ISGH!A1:G80").execute()
        json.dump(gv, open("destaque_isgh.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: destaque_isgh {len(gv.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("destaque_isgh.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler a aba Destaque_ISGH: {e}")
    # Dossie do ISGH (aba ISGH_Dossie da Pipeline Licitacoes, 09/11/2026): o detalhe do contrato
    # dentro da Central, para a equipe nao depender de artefato fora dela.
    try:
        dv2 = sheets.spreadsheets().values().get(spreadsheetId=LICIT_SHEET, range="ISGH_Dossie!A1:E200").execute()
        json.dump(dv2, open("isgh_dossie.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: isgh_dossie {len(dv2.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("isgh_dossie.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler a aba ISGH_Dossie: {e}")
    # Producao dos socios (11/11/2026): tres abas da Pipeline Licitacoes que alimentam a aba
    # "Producao dos socios" da Central. Producao_Params e a regua (coeficientes e pesos),
    # Producao_Socios sao os lancamentos de laudos e Escala_Socios os plantoes.
    # Falha aqui nao derruba a pagina; sem as abas, a aba da Central simplesmente nao aparece.
    try:
        bg = sheets.spreadsheets().values().batchGet(
            spreadsheetId=LICIT_SHEET,
            ranges=["Producao_Params!A1:C60", "Producao_Socios!A1:M500", "Escala_Socios!A1:F300"]
        ).execute()
        vr = bg.get("valueRanges", [])
        prod = {"params": vr[0].get("values", []) if len(vr) > 0 else [],
                "producao": vr[1].get("values", []) if len(vr) > 1 else [],
                "escala": vr[2].get("values", []) if len(vr) > 2 else []}
        json.dump(prod, open("producao.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: producao {len(prod['producao'])} linhas, params {len(prod['params'])}, escala {len(prod['escala'])}")
    except Exception as e:
        json.dump({"params": [], "producao": [], "escala": []}, open("producao.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler as abas de producao dos socios: {e}")
    sys.exit(0)

vals = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Pipeline!A1:AP").execute()
json.dump(vals, open("pipeline.json", "w", encoding="utf-8"), ensure_ascii=False)

# O xlsx do robô do Mac (LICIT_ID) deixou de ser baixado em 02/10/2026: o radar do Mac foi
# aposentado e a planilha Google de licitações é a única fonte.
open("mods.env", "w").write(f"MOD_PIPELINE={mod(PIPELINE_ID)}\n")
print(f"OK: pipeline {len(vals.get('values', []))} linhas")
