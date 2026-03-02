#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_dados.py
==============
Coloque este script na MESMA pasta que index.html e dados.js.

Como usar:
  1. Gere o CSV da rodada (nome padrão: 0_PAINEL_CLAUDE_JOGOS_RODADA_ATUAL.csv)
  2. Coloque o CSV nesta mesma pasta
  3. Execute:  python gerar_dados.py
  4. O arquivo dados.js será atualizado automaticamente
  5. Faça commit e push para o GitHub — o site já estará atualizado!

Opcional — passar nome do CSV como argumento:
  python gerar_dados.py meu_arquivo.csv
"""

import sys
import os
from datetime import datetime

# ── Configurações ────────────────────────────────────────────────────────────
CSV_PADRAO = "0_PAINEL_CLAUDE_JOGOS_RODADA_ATUAL.csv"
SAIDA_JS   = "dados.js"
ENCODING   = "utf-8-sig"   # aceita UTF-8 com ou sem BOM
# ─────────────────────────────────────────────────────────────────────────────


def encontrar_csv(nome_arg=None):
    """Localiza o CSV: argumento CLI > nome padrão > qualquer CSV na pasta."""
    candidatos = []
    if nome_arg:
        candidatos.append(nome_arg)
    candidatos.append(CSV_PADRAO)

    for c in candidatos:
        if os.path.isfile(c):
            return c

    # fallback: primeiro .csv encontrado na pasta
    csvs = [f for f in os.listdir(".") if f.lower().endswith(".csv")]
    if csvs:
        csvs.sort()
        return csvs[0]

    return None


def combinar_datahora(linhas_raw):
    """
    Se o CSV tiver 'Data' e 'Hora_Jg' separados, cria 'DataHora_Jg' combinado.
    Se já tiver 'DataHora_Jg', mantém como está.
    """
    if not linhas_raw:
        return linhas_raw

    header = linhas_raw[0]
    colunas = [c.strip() for c in header.split(",")]

    if "DataHora_Jg" in colunas:
        # já tem o campo combinado — nada a fazer
        return linhas_raw

    if "Data" in colunas and "Hora_Jg" in colunas:
        idx_data = colunas.index("Data")
        idx_hora = colunas.index("Hora_Jg")

        novo_header = "DataHora_Jg," + header.rstrip("\r\n")
        novas = [novo_header]

        for linha in linhas_raw[1:]:
            if not linha.strip():
                continue
            partes = linha.split(",")
            data = partes[idx_data].strip() if idx_data < len(partes) else ""
            hora = partes[idx_hora].strip() if idx_hora < len(partes) else ""
            datahora = (data + " " + hora).strip()
            novas.append(datahora + "," + linha.rstrip("\r\n"))

        return novas

    # CSV sem campos de data reconhecíveis — retorna sem alteração
    return linhas_raw


def gerar_js(csv_path):
    print(f"[✓] Lendo: {csv_path}")

    with open(csv_path, "r", encoding=ENCODING, errors="replace") as f:
        conteudo = f.read()

    linhas_raw = conteudo.splitlines()
    # Remove linhas completamente vazias do início/fim
    while linhas_raw and not linhas_raw[0].strip():
        linhas_raw.pop(0)
    while linhas_raw and not linhas_raw[-1].strip():
        linhas_raw.pop()

    if len(linhas_raw) < 2:
        print("[✗] CSV vazio ou sem dados. Abortando.")
        sys.exit(1)

    linhas = combinar_datahora(linhas_raw)
    n_jogos = len(linhas) - 1  # descontar cabeçalho

    # Escapar backticks dentro do CSV para não quebrar o template literal JS
    csv_seguro = "\n".join(linhas).replace("`", "'").replace("\\", "\\\\")

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    js = f"""/* =============================================================
   dados.js — gerado automaticamente por gerar_dados.py
   Atualizado em: {agora}
   Fonte: {os.path.basename(csv_path)}
   Jogos carregados: {n_jogos}
   ============================================================= */

var CSV_EMBUTIDO = `
{csv_seguro}
`;
"""

    with open(SAIDA_JS, "w", encoding="utf-8") as f:
        f.write(js)

    print(f"[✓] {SAIDA_JS} gerado com {n_jogos} jogos.")
    print(f"[✓] Pronto! Faça commit e push para atualizar o site.")


def main():
    nome_arg = sys.argv[1] if len(sys.argv) > 1 else None
    csv_path = encontrar_csv(nome_arg)

    if not csv_path:
        print("[✗] Nenhum arquivo CSV encontrado na pasta.")
        print(f"    Coloque o CSV aqui ou use: python gerar_dados.py nome_arquivo.csv")
        sys.exit(1)

    gerar_js(csv_path)


if __name__ == "__main__":
    main()
