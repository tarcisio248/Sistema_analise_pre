#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_dados.py — Gera o dados.js a partir do CSV da rodada.
Coloque na mesma pasta que index.html e dados.js.

Uso:
  python gerar_dados.py
  python gerar_dados.py meu_arquivo.csv
"""

import sys, os
from datetime import datetime

CSV_PADRAO = "0_PAINEL_CLAUDE_JOGOS_RODADA_ATUAL.csv"
SAIDA_JS   = "dados.js"

def encontrar_csv(nome_arg=None):
    candidatos = [nome_arg, CSV_PADRAO] if nome_arg else [CSV_PADRAO]
    for c in candidatos:
        if c and os.path.isfile(c):
            return c
    csvs = sorted(f for f in os.listdir(".") if f.lower().endswith(".csv"))
    return csvs[0] if csvs else None

def gerar_js(csv_path):
    print(f"[✓] Lendo: {csv_path}")
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        conteudo = f.read()

    linhas = [l for l in conteudo.strip().splitlines() if l.strip()]
    if len(linhas) < 2:
        print("[✗] CSV vazio. Abortando.")
        sys.exit(1)

    header = linhas[0]
    colunas = [c.strip() for c in header.split(",")]

    # Combinar Data + Hora_Jg em DataHora_Jg se necessário
    if "DataHora_Jg" not in colunas and "Data" in colunas and "Hora_Jg" in colunas:
        idx_d = colunas.index("Data")
        idx_h = colunas.index("Hora_Jg")
        novo_header = "DataHora_Jg," + header.rstrip("\r\n")
        novas = [novo_header]
        for linha in linhas[1:]:
            partes = linha.split(",")
            dh = (partes[idx_d].strip() if idx_d < len(partes) else "") + " " + \
                 (partes[idx_h].strip() if idx_h < len(partes) else "")
            novas.append(dh.strip() + "," + linha.rstrip("\r\n"))
        linhas = novas

    csv_final = "\n".join(linhas).replace("`", "'").replace("\\", "\\\\")
    n_jogos   = len(linhas) - 1
    agora     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    js = f"""/* =============================================================
   dados.js — gerado por gerar_dados.py
   Atualizado em: {agora}
   Fonte: {os.path.basename(csv_path)}
   Jogos: {n_jogos}
   ============================================================= */

var CSV_EMBUTIDO = `
{csv_final}
`;

/* Dispara o carregamento automático no index.html */
if (typeof autoCarregarDados === 'function') {{
  autoCarregarDados();
}}
"""

    with open(SAIDA_JS, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"[✓] {SAIDA_JS} gerado com {n_jogos} jogos!")
    print(f"[✓] Agora faça: git add dados.js && git commit -m 'nova rodada' && git push")

if __name__ == "__main__":
    csv = encontrar_csv(sys.argv[1] if len(sys.argv) > 1 else None)
    if not csv:
        print("[✗] Nenhum CSV encontrado.")
        sys.exit(1)
    gerar_js(csv)
