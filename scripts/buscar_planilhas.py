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
    # Contratos TRX (12/11/2026): aba Contratos da planilha Documentos TRX, para a area
    # Fiscal e Juridico da Central (Henrique e Ana). Falha aqui nao derruba a pagina.
    try:
        cv = sheets.spreadsheets().values().get(spreadsheetId=DOCS_SHEET, range="Contratos!A1:N200").execute()
        json.dump(cv, open("contratos.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: contratos {len(cv.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("contratos.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler a aba Contratos: {e}")
    # Producao dos socios (11/11/2026): tres abas da Pipeline Licitacoes que alimentam a aba
    # "Producao dos socios" da Central. Producao_Params e a regua (coeficientes e pesos),
    # Producao_Socios sao os lancamentos de laudos e Escala_Socios os plantoes.
    # Falha aqui nao derruba a pagina; sem as abas, a aba da Central simplesmente nao aparece.
    try:
        bg = sheets.spreadsheets().values().batchGet(
            spreadsheetId=LICIT_SHEET,
            ranges=["Producao_Params!A1:C120", "Producao_Socios!A1:M500", "Escala_Socios!A1:F300"]
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
    # Banco de entregas do HRVJ (17/11/2026): aba Entregas_HRVJ, escrita pelo app de Edicao v17 quando
    # a Carla guarda a entrega na aba Relatorios. So saem Emissao e Total. Falha nao derruba a pagina.
    try:
        ev = sheets.spreadsheets().values().get(spreadsheetId=LICIT_SHEET, range="Entregas_HRVJ!A1:B400").execute()
        json.dump(ev, open("entregas_hrvj.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: entregas_hrvj {len(ev.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("entregas_hrvj.json", "w", encoding="utf-8"))
        print(f"::warning::Nao consegui ler a aba Entregas_HRVJ: {e}")
    # Banco de entregas por hospital e modalidade (20/11/2026): aba Entregas_Geral, criada pelo app de
    # Edicao v18 na primeira entrega de um hospital ou modalidade que nao seja a RM do HRVJ.
    # Colunas: Contrato | Modalidade | Emissao | Total. Enquanto a aba nao existe, segue sem aviso.
    try:
        eg = sheets.spreadsheets().values().get(spreadsheetId=LICIT_SHEET, range="Entregas_Geral!A1:D3000").execute()
        json.dump(eg, open("entregas_geral.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"OK: entregas_geral {len(eg.get('values', []))} linhas")
    except Exception as e:
        json.dump({"values": []}, open("entregas_geral.json", "w", encoding="utf-8"))
        print(f"Aba Entregas_Geral ainda nao existe ou nao foi lida: {e}")
    sys.exit(0)

vals = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Pipeline!A1:AP").execute()
json.dump(vals, open("pipeline.json", "w", encoding="utf-8"), ensure_ascii=False)
# Mural da equipe (15/11/2026): aba Mural da Pipeline TRX, escrita pelo app de Edição v13.
# Falha aqui não derruba a página; sem a aba, o bloco do mural simplesmente não aparece.
try:
    mv = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Mural!A1:D400").execute()
    json.dump(mv, open("mural.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"OK: mural {len(mv.get('values', []))} linhas")
except Exception as e:
    json.dump({"values": []}, open("mural.json", "w", encoding="utf-8"))
    print(f"::warning::Nao consegui ler a aba Mural: {e}")

# Feito, Ciente e Observação das tarefas do bloco Hoje (16/11/2026): aba Tarefas_Status, escrita pelo app v14.
try:
    tv = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Tarefas_Status!A1:H5000").execute()
    json.dump(tv, open("tarefas.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"OK: tarefas {len(tv.get('values', []))} linhas")
except Exception as e:
    json.dump({"values": []}, open("tarefas.json", "w", encoding="utf-8"))
    print(f"::warning::Nao consegui ler a aba Tarefas_Status: {e}")

# Equipe e Objetivos da semana (17/11/2026): contatos da equipe e objetivos na aba Início.
# Da aba Equipe só saem Nome, Email, Apelido, Ativo, Papel e Telefone; a coluna PIN não é lida.
try:
    ev = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Equipe!A1:F80").execute()
    json.dump(ev, open("equipe.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"OK: equipe {len(ev.get('values', []))} linhas")
except Exception as e:
    json.dump({"values": []}, open("equipe.json", "w", encoding="utf-8"))
    print(f"::warning::Nao consegui ler a aba Equipe: {e}")
try:
    ov = sheets.spreadsheets().values().get(spreadsheetId=PIPELINE_ID, range="Objetivos!A1:H600").execute()
    json.dump(ov, open("objetivos.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"OK: objetivos {len(ov.get('values', []))} linhas")
except Exception as e:
    json.dump({"values": []}, open("objetivos.json", "w", encoding="utf-8"))
    print(f"::warning::Nao consegui ler a aba Objetivos: {e}")

# O xlsx do robô do Mac (LICIT_ID) deixou de ser baixado em 02/10/2026: o radar do Mac foi
# aposentado e a planilha Google de licitações é a única fonte.
open("mods.env", "w").write(f"MOD_PIPELINE={mod(PIPELINE_ID)}\n")
print(f"OK: pipeline {len(vals.get('values', []))} linhas")
