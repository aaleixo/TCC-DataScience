"""Monta o conjunto de desenvolvimento v0 (pares) a partir das linhas coletadas no site Economiza Alagoas.
Entrada: linhas 'descricao<TAB>codigo_barras<TAB>rede<TAB>ocorrencias'. Semente fixa para reprodutibilidade."""
import csv, json, random, re, sys, unicodedata, itertools, collections

SEMENTE = 20261123
random.seed(SEMENTE)
META = {"positivo": 160, "negativo_dificil": 160, "negativo_aleatorio": 60}
MAX_POR_CODIGO = 4
MAX_POR_TERMO = 25  # equilibra as categorias de busca

def ler(caminhos):
    linhas = []
    for c in caminhos:
        txt = open(c, encoding="utf-8").read()
        try:
            j = json.loads(txt)
            if isinstance(j, list):
                t = j[0]["text"]
                t = t[: t.rfind('"') + 1] if "(captured at origin" in t else t
                txt = json.loads(t)
        except Exception as e:
            pass  # arquivo TSV simples
        for l in txt.split("\n"):
            p = l.split("\t")
            if len(p) >= 4 and p[3].isdigit():
                linhas.append({"desc": p[0].strip(), "cb": p[1].strip(), "rede": p[2].strip(), "n": int(p[3] or 1),
                               "termo": p[4].strip() if len(p) > 4 else ""})
    return linhas

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"\s+", " ", re.sub(r"[^A-Z0-9 ]", " ", s)).strip()

def tokens(s):
    return {t for t in norm(s).split() if len(t) > 1}

def gtin_valido(cb):
    if not re.fullmatch(r"\d{8}|\d{12,14}", cb):
        return False
    d = [int(x) for x in cb]
    soma = sum(v * (3 if i % 2 == 0 else 1) for i, v in enumerate(reversed(d[:-1])))
    return (10 - soma % 10) % 10 == d[-1]

def main(caminhos, saida):
    linhas = ler(caminhos)
    total = len(linhas)
    linhas = [l for l in linhas if gtin_valido(l["cb"]) and not l["cb"].startswith("2")]
    # uma descrição por (código, rede, descrição normalizada)
    vistos, itens = set(), []
    for l in linhas:
        k = (l["cb"], l["rede"], norm(l["desc"]))
        if k not in vistos:
            vistos.add(k); itens.append(l)
    por_cb = collections.defaultdict(list)
    for it in itens:
        por_cb[it["cb"]].append(it)

    pares, usados = [], set()
    por_termo_estrato = collections.Counter()
    def add(a, b, estrato, verdade):
        termo = a["termo"] or b["termo"]
        if por_termo_estrato[(estrato, termo)] >= MAX_POR_TERMO:
            return False
        k = tuple(sorted([(a["cb"], a["rede"], norm(a["desc"])), (b["cb"], b["rede"], norm(b["desc"]))]))
        if k in usados or norm(a["desc"]) == norm(b["desc"]) or a["rede"] == b["rede"]:
            return False
        usados.add(k)
        por_termo_estrato[(estrato, termo)] += 1
        if random.random() < 0.5:
            a, b = b, a
        pares.append({"descricao_a": a["desc"], "descricao_b": b["desc"], "codigo_a": a["cb"], "codigo_b": b["cb"],
                      "rede_a": a["rede"], "rede_b": b["rede"], "termo": a["termo"] or b["termo"],
                      "estrato": estrato, "verdade_por_codigo": verdade})
        return True

    # positivos: mesmo código, redes diferentes, descrições diferentes
    cbs = [c for c, v in por_cb.items() if len({x["rede"] for x in v}) >= 2]
    random.shuffle(cbs)
    cand_pos = []
    for c in cbs:
        combos = [(a, b) for a, b in itertools.combinations(por_cb[c], 2)
                  if a["rede"] != b["rede"] and norm(a["desc"]) != norm(b["desc"])]
        random.shuffle(combos)
        cand_pos.append(combos[:MAX_POR_CODIGO])
    for rodada in range(MAX_POR_CODIGO):
        for combos in cand_pos:
            if rodada < len(combos) and sum(p["estrato"] == "positivo" for p in pares) < META["positivo"]:
                add(*combos[rodada], "positivo", 1)

    # negativos difíceis: códigos diferentes, mesmo termo de busca, vocabulário parecido (Jaccard >= 0,4)
    reps = [random.choice(v) for v in por_cb.values()]
    cand_neg, cont = [], collections.Counter()
    for a, b in itertools.combinations(reps, 2):
        if a["cb"] == b["cb"] or a["termo"] != b["termo"]:
            continue
        ta, tb = tokens(a["desc"]), tokens(b["desc"])
        j = len(ta & tb) / max(1, len(ta | tb))
        if j >= 0.4:
            cand_neg.append((j, a, b))
    random.shuffle(cand_neg)
    for j, a, b in cand_neg:
        if sum(p["estrato"] == "negativo_dificil" for p in pares) >= META["negativo_dificil"]:
            break
        if cont[a["cb"]] < MAX_POR_CODIGO and cont[b["cb"]] < MAX_POR_CODIGO:
            if add(a, b, "negativo_dificil", 0):
                cont[a["cb"]] += 1; cont[b["cb"]] += 1

    # negativos aleatórios: mesmo termo de busca, códigos diferentes
    por_termo = collections.defaultdict(list)
    for r in reps:
        por_termo[r["termo"]].append(r)
    tentativas = 0
    while sum(p["estrato"] == "negativo_aleatorio" for p in pares) < META["negativo_aleatorio"] and tentativas < 10000:
        tentativas += 1
        t = random.choice(list(por_termo))
        if len(por_termo[t]) < 2:
            continue
        a, b = random.sample(por_termo[t], 2)
        if a["cb"] != b["cb"]:
            add(a, b, "negativo_aleatorio", 0)

    random.shuffle(pares)
    for i, p in enumerate(pares, 1):
        p["par_id"] = f"dev0-{i:04d}"
    campos = ["par_id", "descricao_a", "descricao_b", "estrato", "verdade_por_codigo", "verdade_revisada",
              "decidivel_texto", "observacao", "codigo_a", "codigo_b", "rede_a", "rede_b", "termo"]
    with open(saida + "_para_rotular.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore"); w.writeheader()
        for p in pares:
            w.writerow({**p, "verdade_revisada": "", "decidivel_texto": "", "observacao": ""})
    with open(saida + "_sem_rotulo.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["par_id", "descricao_a", "descricao_b"], extrasaction="ignore"); w.writeheader()
        for p in pares:
            w.writerow(p)
    est = collections.Counter(p["estrato"] for p in pares)
    print(f"linhas lidas {total} | com GTIN válido {len(linhas)} | itens únicos {len(itens)} | códigos {len(por_cb)} "
          f"| códigos em 2+ redes {len(cbs)}")
    print("pares:", dict(est), "| total", len(pares))

if __name__ == "__main__":
    main(sys.argv[2:], sys.argv[1])
