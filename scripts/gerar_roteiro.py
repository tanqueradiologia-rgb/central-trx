#!/usr/bin/env python3
"""Gera site/roteiro.js (Central) e o bloco ROTEIRO do apps-script/Codigo.gs (app de Edição) a partir de config/roteiro.json.
Rode depois de mudar o roteiro: python3 scripts/gerar_roteiro.py"""
import json, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = json.load(open(os.path.join(RAIZ, "config", "roteiro.json"), encoding="utf-8"))
js = json.dumps(r, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(RAIZ, "site", "roteiro.js"), "w", encoding="utf-8").write(
    "/* gerado por scripts/gerar_roteiro.py a partir de config/roteiro.json: não edite aqui */\nwindow.ROTEIRO=" + js + ";\n")
# no app de Edição o roteiro vai dentro do Codigo.gs, entre os marcadores (um arquivo só para colar no editor)
gs = os.path.join(RAIZ, "apps-script", "Codigo.gs")
s = open(gs, encoding="utf-8").read()
a, b = "// ROTEIRO-INICIO", "// ROTEIRO-FIM"
i, j = s.index(a), s.index(b)
s = s[:i] + a + " (gerado por scripts/gerar_roteiro.py a partir de config/roteiro.json: não edite aqui)\nconst ROTEIRO = " + js + ";\n" + s[j:]
open(gs, "w", encoding="utf-8").write(s)
print("roteiro.js e Codigo.gs atualizados,", len(js), "bytes")
