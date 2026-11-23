# Acompanhamento do TCC

Atualizado em 23/11/2026. O status das tarefas fica no Linear (projeto P-CON-6, cards CON-5 a CON-27).

## Linha do tempo

| Data | O que aconteceu |
|---|---|
| 19/11/2026 | O Prof. Rangel recomendou o tema de normalização de produtos de cupons fiscais (origem: projeto PreçoBom) |
| 21/11/2026 | Proposta v1 enviada ao orientador (`docs/proposta/proposta_v1_enviada_2026-11-21.pdf`) |
| 21/11/2026 | Primeira revisão adversarial (Fable) → rascunho da v2 |
| 22/11/2026 | Teste do site Economiza Alagoas: descrições são as originais de cada loja (Fermento Royal 250g: 15 lojas, 8 descrições). Pedido de token enviado a api@sefaz.al.gov.br |
| 22–23/11/2026 | Teste com 6 cupons de SP (4 redes): EAN só aparece em 1 rede; nenhum produto idêntico entre redes |
| 23/11/2026 | Testes do LLM no Colab (v1 a v3); segunda revisão adversarial (Fable); v2 atualizada |
| 23/11/2026 | Coleta pelo site (8 buscas, 13.694 linhas) e conjunto de desenvolvimento v0 (380 pares) |

## Decisões fechadas

- Métrica principal: risco de falso positivo (erro silencioso), com limite superior de Clopper-Pearson; X esperado entre 3% e 5%.
- Quatro métodos invariantes à ordem: textual com regras, embeddings, regressão logística e LLM local simetrizado nas duas ordens.
- LLM: prompt binário com tokens "Sim"/"Não" (menor inversão entre ordens e prior negativo no teste v3); 3B em 4 bits descartado (mais instável que em float16).
- Lista fechada do LLM para o pré-registro: modelo (3B float16 ou 7B) × operador das duas ordens (média ou mínimo). A versão do 7B (4 bits na T4 ou float16 na L4) depende do teste v4.
- Pares só entre redes diferentes; divisão por marca × categoria; desenvolvimento em duas partes; pré-registro em commit datado neste repositório antes de abrir o teste.
- A rotulação é feita pela autora, não por um modelo.
- Orçamento zero; ambiente de experimentos: Google Colab.

## Pendências

- Resposta do orientador à v1 (CEP, orientação).
- Token da API Economiza Alagoas (controle em 28/11, 01/12 e 05/12; plano B: site público).
- Rotulação do conjunto v0 (coluna "decidível só pelo texto" em todos os pares).
- Teste v4 (7B em float16 na L4).
