#!/usr/bin/env python3
"""Cifra os dados da Central (dados_central.js, saude.js e roteiro.js) num único
arquivo site/central.enc, lido pela página com a senha da equipe.

Uso:  CENTRAL_SENHA=... python scripts/cifrar_central.py
Os três arquivos em texto claro são apagados de site/ depois de cifrados, para o
GitHub Pages publicar só o pacote cifrado.

Formato de central.enc (JSON): {"v":1,"kdf":"pbkdf2-sha256","iter":N,"salt":b64,"iv":b64,"ct":b64}
Chave: PBKDF2-HMAC-SHA256 (senha, salt, N) de 256 bits. Cifra: AES-256-GCM.
A página decifra com Web Crypto (SubtleCrypto) e executa o JS resultante.
"""
import base64, json, os, sys

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, "site")
ARQUIVOS = ["dados_central.js", "saude.js", "roteiro.js"]
ITER = 150_000

senha = os.environ.get("CENTRAL_SENHA", "")
if len(senha) < 8:
    print("CENTRAL_SENHA ausente ou com menos de 8 caracteres: a Central não foi cifrada.", file=sys.stderr)
    sys.exit(1)

partes = []
for nome in ARQUIVOS:
    p = os.path.join(SITE, nome)
    if os.path.exists(p):
        partes.append("/* " + nome + " */\n" + open(p, encoding="utf-8").read())
    else:
        partes.append("/* " + nome + " ausente */\n")
claro = "\n".join(partes).encode("utf-8")

salt = os.urandom(16)
iv = os.urandom(12)
chave = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(senha.encode("utf-8"))
ct = AESGCM(chave).encrypt(iv, claro, None)

b64 = lambda b: base64.b64encode(b).decode("ascii")
saida = {"v": 1, "kdf": "pbkdf2-sha256", "iter": ITER, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}
open(os.path.join(SITE, "central.enc"), "w", encoding="utf-8").write(json.dumps(saida))

for nome in ARQUIVOS:
    p = os.path.join(SITE, nome)
    if os.path.exists(p):
        os.remove(p)

print("central.enc gerado:", len(claro), "bytes em claro,", len(ct), "bytes cifrados; arquivos em claro removidos de site/")
