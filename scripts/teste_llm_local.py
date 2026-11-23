"""
Teste técnico do TCC: velocidade e log-probabilidades de um LLM local (llama.cpp).

Pré-requisito: llama-server rodando em http://127.0.0.1:8080 (veja o roteiro).
Uso:  python teste_llm_local.py
Saída: tabela no terminal e o arquivo resultado_teste_llm.csv na mesma pasta.
"""
import csv
import math
import statistics
import time

import requests

URL = "http://127.0.0.1:8080/v1/chat/completions"
REPETICOES = 3  # cada par roda 3 vezes, para medir tempo e conferir estabilidade

INSTRUCAO = (
    "Você compara descrições de produtos de cupons fiscais de supermercados brasileiros. "
    "Duas descrições são o MESMO produto somente se tiverem a mesma marca, a mesma variante "
    "(tipo, sabor, versão) e o mesmo conteúdo (peso ou volume). "
    "Responda apenas com um dígito: 1 se forem o mesmo produto, 0 se forem produtos diferentes."
)

# (descrição A, descrição B, rótulo esperado: 1 = mesmo produto, 0 = diferente, None = não decidível pelo texto)
PARES = [
    ("FERM.ROYAL", "FERMENTO ROYAL 250G", 1),
    ("FERM PO ROYAL 250G", "FERMENTO EM P ROYAL 250G", 1),
    ("BISC RECH MOCA 140G NESTLE", "BIS REC NESTLE MOCA 140G", 1),
    ("MOCA Biscoito Recheado 140g", "BISCOITO RECH. MOCA 140G", 1),
    ("AG CRYSTAL C/G 1,5L", "AG CRYSTAL S/G 1,5L", 0),
    ("LEITE IN XANDO LIGHT GFA 1LT", "LEITE IN XANDO TIPO A GFA 1LT", 0),
    ("ATUM 88 SOL NAT 140G", "ATUM 88 SOLI 140G", 0),
    ("PE DE MOCA AMENDOIM E LEITE CONDENSADO POPULAR 55G", "LEITE COND MOCA", 0),
    ("LEITE COND. MOCA SEMIDESN. TP 395G", "LEITE COND SEMID MOCA TRAD TP 395G", 1),
    ("MOLHO BILLY E JACK 200G OR", "MOLHO BILLY E JACK 200G TA", None),
]


def perguntar(a: str, b: str) -> dict:
    corpo = {
        "messages": [
            {"role": "system", "content": INSTRUCAO},
            {"role": "user", "content": f"Descrição A: {a}\nDescrição B: {b}\nResposta:"},
        ],
        "max_tokens": 1,
        "temperature": 0,
        "seed": 42,
        "logprobs": True,
        "top_logprobs": 10,
    }
    inicio = time.perf_counter()
    r = requests.post(URL, json=corpo, timeout=300)
    segundos = time.perf_counter() - inicio
    r.raise_for_status()
    escolha = r.json()["choices"][0]
    resposta = escolha["message"]["content"].strip()

    # Probabilidade de "1" e de "0" no primeiro token gerado
    lp = {"1": None, "0": None}
    try:
        for cand in escolha["logprobs"]["content"][0]["top_logprobs"]:
            tok = cand["token"].strip()
            if tok in lp and lp[tok] is None:
                lp[tok] = cand["logprob"]
    except (KeyError, IndexError, TypeError):
        pass

    if lp["1"] is not None and lp["0"] is not None:
        p1, p0 = math.exp(lp["1"]), math.exp(lp["0"])
        p_mesmo = p1 / (p1 + p0)
    elif lp["1"] is not None:
        p_mesmo = 1.0
    elif lp["0"] is not None:
        p_mesmo = 0.0
    else:
        p_mesmo = None  # log-probabilidades não vieram
    return {"resposta": resposta, "p_mesmo": p_mesmo, "segundos": segundos}


def main():
    try:
        info = requests.get("http://127.0.0.1:8080/v1/models", timeout=10).json()
        modelo = info["data"][0]["id"]
    except Exception:
        print("Não encontrei o llama-server em http://127.0.0.1:8080. Ele está aberto?")
        return
    print(f"Modelo: {modelo}\n")

    linhas, tempos = [], []
    for a, b, esperado in PARES:
        for rep in range(1, REPETICOES + 1):
            res = perguntar(a, b)
            tempos.append(res["segundos"])
            linhas.append({"modelo": modelo, "descricao_a": a, "descricao_b": b,
                           "esperado": "" if esperado is None else esperado,
                           "repeticao": rep, **res})
        ult = linhas[-1]
        p = "sem logprob" if ult["p_mesmo"] is None else f"p(mesmo)={ult['p_mesmo']:.3f}"
        print(f"[{'?' if esperado is None else esperado}] resp={ult['resposta']!r:4} {p:18} "
              f"{ult['segundos']:.1f}s  |  {a}  ×  {b}")

    with open("resultado_teste_llm.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)

    # A primeira chamada inclui aquecimento; a mediana é a medida mais justa
    print(f"\nTempo por par: mediana {statistics.median(tempos):.2f}s, "
          f"máximo {max(tempos):.2f}s, mínimo {min(tempos):.2f}s")
    print(f"Estimativa para 1.500 pares: {statistics.median(tempos) * 1500 / 60:.0f} minutos")
    estaveis = all(len({round(l['p_mesmo'] or -1, 4) for l in linhas
                        if l['descricao_a'] == a and l['descricao_b'] == b}) == 1
                   for a, b, _ in PARES)
    print(f"Mesma probabilidade nas {REPETICOES} repetições de cada par: {'sim' if estaveis else 'NÃO'}")
    print("Arquivo salvo: resultado_teste_llm.csv")


if __name__ == "__main__":
    main()
