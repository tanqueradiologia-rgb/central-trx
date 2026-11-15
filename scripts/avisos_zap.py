# -*- coding: utf-8 -*-
"""Avisos da Central no zap da equipe (regra do Marcos, 15/11/2026).

Depois que o build gera site/dados_central.js, este script compara o que a
Central mostra com o estado da última rodada (data/avisos_state.json) e manda
no WhatsApp, pelo numero da TRX (Cloud API da Meta), um aviso por item NOVO:

- documento VENCIDO: avisa a Carla (com a marca de que o Marcos regulariza)
  e o Marcos (REGULARIZAR AGORA);
- documento que entrou na faixa VENCE EM 15 DIAS: avisa a Carla;
- documento marcado DESATUALIZADO (coluna T): avisa a Carla.

Sem os segredos ZAP_TOKEN/ZAP_PHONE_ID/ZAP_CONTATOS o script nao faz nada e
nao mexe no estado: quando o Marcos ativar o zap, a fila acumulada sai aos
poucos (ate 8 avisos por rodada). Item que sai da Central sai do estado.
"""
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(BASE, "site", "dados_central.js")
STATE = os.path.join(BASE, "data", "avisos_state.json")
MAX_POR_RODADA = 8


def carrega_central():
    t = open(DADOS, encoding="utf-8").read()
    return json.loads(t[t.index("=") + 1:].strip().rstrip(";"))


def monta_avisos(central):
    """Lista de (chave, apelido, texto). A chave identifica o item na Central."""
    avisos = []
    for d in central.get("documentos_alerta", []):
        doc = (d.get("doc") or "").strip()
        val = (d.get("val") or "").strip()
        if not doc:
            continue
        if d.get("venc"):
            chave = f"doc-venc:{doc}:{val}"
            quando = f" (vencido em {val})" if val else ""
            avisos.append((chave, "carla",
                           f"Central TRX: {doc} VENCIDO{quando}. O Marcos vai regularizar; acompanhe pela Central."))
            avisos.append((chave + "#marcos", "marcos",
                           f"Central TRX: REGULARIZAR AGORA {doc}{quando}."))
        elif (d.get("breve") or "").upper().startswith("VENCE EM 15"):
            chave = f"doc-15:{doc}:{val}"
            quando = f" ({val})" if val else ""
            avisos.append((chave, "carla",
                           f"Central TRX: {doc} vence em 15 dias{quando}. Renovar na faixa."))
        elif d.get("mot"):
            chave = f"doc-desat:{doc}"
            avisos.append((chave, "carla",
                           f"Central TRX: {doc} DESATUALIZADO. {str(d['mot'])[:140]}"))
    return avisos


def envia(token, phone_id, numero, texto):
    payload = {"messaging_product": "whatsapp", "to": numero, "type": "template",
               "template": {"name": "aviso_trx", "language": {"code": "pt_BR"},
                            "components": [{"type": "body",
                                            "parameters": [{"type": "text",
                                                            "text": texto.replace("\n", " ")}]}]}}
    req = urllib.request.Request(
        f"https://graph.facebook.com/v21.0/{phone_id}/messages",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)


def main():
    central = carrega_central()
    avisos = monta_avisos(central)
    chaves_atuais = {a[0] for a in avisos}

    state = {"notificados": {}}
    if os.path.exists(STATE):
        state = json.load(open(STATE, encoding="utf-8"))
    notificados = state.get("notificados", {})

    novos = [a for a in avisos if a[0] not in notificados]

    token = os.environ.get("ZAP_TOKEN", "")
    phone_id = os.environ.get("ZAP_PHONE_ID", "")
    contatos = json.loads(os.environ.get("ZAP_CONTATOS") or "{}")
    if not (token and phone_id and contatos):
        print(f"zap desativado (sem segredos); {len(novos)} aviso(s) aguardando ativacao")
        return 0

    enviados = 0
    gerado = central.get("gerado", "")
    for chave, apelido, texto in novos[:MAX_POR_RODADA]:
        numero = contatos.get(apelido, "")
        if not numero:
            print(f"sem numero para '{apelido}' no ZAP_CONTATOS; aviso retido: {chave}")
            continue
        try:
            envia(token, phone_id, numero, texto)
            notificados[chave] = gerado
            enviados += 1
            print(f"enviado a {apelido}: {chave}")
        except urllib.error.HTTPError as e:
            print(f"ERRO ao enviar {chave}: HTTP {e.code} {e.read().decode()[:300]}")

    # item que saiu da Central sai do estado (se voltar, avisa de novo)
    notificados = {k: v for k, v in notificados.items() if k in chaves_atuais}
    state["notificados"] = notificados
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"rodada: {len(avisos)} item(ns) na Central, {len(novos)} novo(s), {enviados} enviado(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
