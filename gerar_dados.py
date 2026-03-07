#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, csv, io, json, re
from datetime import datetime

CSV_PADRAO = "0_PAINEL_CLAUDE_JOGOS_RODADA_ATUAL.csv"
HTML_BASE  = "analise_forcas_csv.html"
SAIDA_HTML = "index.html"

def encontrar_csv(nome_arg=None):
    for c in ([nome_arg] if nome_arg else []) + [CSV_PADRAO]:
        if c and os.path.isfile(c): return c
    csvs = sorted(f for f in os.listdir(".") if f.lower().endswith(".csv"))
    return csvs[0] if csvs else None

def encontrar_template():
    for nome in [HTML_BASE, "index_base.html", SAIDA_HTML]:
        if os.path.isfile(nome): return nome
    return None

def processar_csv(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()
    reader = csv.reader(io.StringIO(content))
    headers = next(reader)
    result = []
    for row in reader:
        if not any(v.strip() for v in row): continue
        obj = {h.strip(): v.strip() for h, v in zip(headers, row)}
        obj["DataHora_Jg"] = f"{obj.get('Data','')} {obj.get('Hora_Jg','')}".strip()
        result.append(obj)
    return result

def gerar_html(jogos, template_path):
    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()
    html = html.replace(
        "mercado: gv(r,m,'Met_sugerido','Met sugerido','Mercado','mercado'),",
        "mercado: gv(r,m,'Met_sugerido','Met_final','Met sugerido','Mercado','mercado'),"
    )
    html = re.sub(r'\n<script>\n/\* RODADA \d+ \*/.*?</script>', '', html, flags=re.DOTALL)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    jogos_json = json.dumps(jogos, ensure_ascii=False)
    injetar = f"""
<script>
/* RODADA {ts} */
(function(){{
  var JOGOS={jogos_json};
  function csvDeJogos(j){{
    if(!j||!j.length) return '';
    var h=Object.keys(j[0]),L=[h.join(',')];
    j.forEach(function(r){{
      L.push(h.map(function(k){{
        var v=r[k]!==undefined?String(r[k]):'';
        return(v.indexOf(',')>=0||v.indexOf('"')>=0)?'"'+v.replace(/"/g,'""')+'"':v;
      }}).join(','));
    }});
    return L.join('\\n');
  }}
  function tentarCarregar(){{
    if(typeof processarCSV==='function') processarCSV(csvDeJogos(JOGOS));
    else setTimeout(tentarCarregar,50);
  }}
  document.readyState==='loading'
    ?document.addEventListener('DOMContentLoaded',tentarCarregar)
    :tentarCarregar();
}})();
</script></body></html>"""
    html = html.rstrip()
    for tag in ["</html>", "</body>"]:
        if html.endswith(tag):
            html = html[:-len(tag)].rstrip()
    return html + injetar

def main():
    csv_path = encontrar_csv(sys.argv[1] if len(sys.argv) > 1 else None)
    if not csv_path:
        print("[X] CSV nao encontrado."); sys.exit(1)
    template = encontrar_template()
    if not template:
        print("[X] Template HTML nao encontrado."); sys.exit(1)
    print(f"[OK] CSV: {csv_path} | Template: {template}")
    jogos = processar_csv(csv_path)
    print(f"[OK] {len(jogos)} jogos processados")
    html = gerar_html(jogos, template)
    with open(SAIDA_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] {SAIDA_HTML} gerado!")

if __name__ == "__main__":
    main()
