Vou recalcular os números a partir dos dois CSVs e abrir a literatura sobre viés de ordem antes de montar a revisão. Um aviso desde já: a proposta em PDF não chegou, só os dois CSVs.

**Veredito:** a regra proposta (item 5) pode até estar certa, mas esses 15 pares não a sustentam. Recalculando os CSVs, três das cinco interpretações dependem de 1 ou 2 pares, e o teste quase não informa sobre a métrica principal (falso positivo). A proposta em PDF não chegou, então não conferi nada contra ela.

## Fatos recalculados dos CSVs

- **Acurácia pelo sinal da média:** 12/15 no 7B e 12/15 no 3B.
- **Ordens isoladas no 7B:** A×B acerta 11/15 e B×A acerta 14/15; o único erro de B×A é FERM.ROYAL, o par não decidível. A média transformou dois acertos de B×A (FERM PO e FERMENTO POTE) em erros marginais (−2,44 e −0,62).
- **Mediana "16,3 vs 1,5":** só reproduz excluindo os dois pares não decidíveis. Com os 15, os erros do 7B têm |média| de 15,0, 2,44 e 0,62. FERM.ROYAL erra com as duas ordens concordando (−11,6 e −18,4).
- **Falsos positivos:** os três erros do 7B pela média são falsos negativos. O único FP do 7B aparece em A×B isolada (BILLY E JACK, +5,87), e a média o segura por 0,56. O 3B tem um FP com as duas ordens concordando (ATUM, +18,2 e +13,3).
- **Direção do efeito de ordem:** a diferença B×A − A×B tem média de +2,05 (7B) e +0,56 (3B), contra variação por par de −13 a +29. Inversões de sinal: 3 no 7B, 1 no 3B.
- **Resolução do escore:** todos os log-odds do 7B são múltiplos de 0,125; os do 3B, de 1/64.
- **`tri_massa`:** vale ≈1,0 em todas as linhas, ou seja, as probabilidades foram renormalizadas entre os três tokens.
- **Tempo médio das 3 chamadas:** 1,34 s no 7B e 0,39 s no 3B.

## Tabela de problemas

A coluna "por que importa" é fato quando cita número; o resto é julgamento meu.

| Ponto | Gravidade | Por que importa | O que fazer | Custo (h) |
|---|---|---|---|---|
| O teste não mede a métrica principal | Crítica | Há 9 negativos e 0 ou 1 FP por configuração. Zero FP em 9 dá limite superior unilateral de 95% de cerca de 28%. | Montar um conjunto de desenvolvimento rotulado por código de barras, rico em negativos difíceis (mesma marca, variante diferente). | 1 |
| Regra criada depois de ver os dados | Crítica | Os 15 pares geraram a hipótese; não podem também confirmá-la. | Tratá-los como exploratórios no texto e confirmar em dados novos antes do pré-registro. | 0 |
| Exclusão dos não decidíveis na estatística de separação | Crítica | FERM.ROYAL é o contraexemplo da tese "discordância = dúvida", e saiu da conta. No teste final esses pares estarão presentes. | Reportar com todos os pares. Afirmar só que concordância entre ordens detecta instabilidade, não erro sistemático. | 0 |
| "Viés de posição" é o nome errado | Importante | A direção média é quase nula e muda de par para par. Isso é sensibilidade à ordem, não preferência por uma posição. | Medir taxa de inversão e direção média, com IC, no conjunto novo. Usar "order sensitivity" no texto. | 0,25 |
| Média vs. melhor ordem isolada | Importante | No 7B, B×A sozinha bate a média. Pode ser acaso, ou assimetria de conteúdo (qual descrição é a abreviada). | Comparar A×B, B×A, média e mínimo das duas ordens. O mínimo é o operador conservador natural para FP. | 0,5 |
| Trocar A e B não cancela o prior dos rótulos | Importante | O significado de "0" e "1" não muda na troca. Os três erros do 7B vão para "0", o que é compatível com prior para "0" ou só com pares difíceis. | Rodar uma variante com rótulos invertidos ou "sim/não". Um limiar ajustado absorve viés constante, mas isso precisa ser dito. | 0,5 |
| Leitura do primeiro token não auditada | Importante | Sem a massa absoluta em {0,1}, não se sabe se o modelo queria começar por outro token. | Registrar a massa absoluta e a taxa de divergência entre o argmax do primeiro token e o texto gerado. | 0,5 |
| "7B entende melhor abreviações" | Importante | Baseia-se em 1 par (ATUM). O 7B erra FERMENTO POTE, que o 3B acerta com +14,9. Tamanho está confundido com quantização. | Rodar o 3B também em 4 bits. Não afirmar superioridade sem o conjunto novo. | 0,25 |
| "Superconfiante, não serve para abster" | Importante | Magnitude não é calibração, e abstenção depende de ordenação, não de escala. Em B×A, o único erro do 7B é o par não decidível. | Avaliar por curva risco–cobertura. Escala se corrige depois com Platt ou temperatura, sem mudar a ordenação. | 0 |
| Resolução de 0,125 no 7B | Menor | O par BILLY E JACK fica a cerca de 4 passos de zero. O padrão sugere bfloat16 na saída (inferência minha). | Conferir e fixar o dtype de computação; registrar no pré-registro. | 0,1 |
| Motivo do descarte do prompt de três opções | Menor | Diferir entre modelos é esperado. O argumento que vale é outro: no 7B ele gera 2 FPs (ATUM e BILLY E JACK) e a opção 2 nunca vence. | Trocar a justificativa no texto. | 0 |

## Respostas às perguntas 2, 4 e 5

**2. A média é defensável?** Sim, como simetrização: "mesmo produto" é uma relação simétrica, então f(A,B) deveria ser igual a f(B,A). Agregar as duas ordens tem precedente direto em LLM-as-judge e ranking (referências abaixo). Há três ressalvas para o artigo:

- Chame de sensibilidade à ordem, a menos que os dados novos mostrem uma direção.
- Média de log-odds, média de probabilidades e "concorda ou abstém" são operadores diferentes; escolha um e justifique.
- A troca não cancela o prior dos rótulos.

Em entity matching especificamente, só achei dois trabalhos que trocam a ordem dos registros. Nenhum mede o efeito em escore de primeiro token de LLM generativo local, então sua medição vira uma contribuição pequena se feita em dados limpos.

**4. Pré-registro.**

- **Fixar agora:**
  - modelo, revisão, quantização e dtype;
  - texto literal dos prompts e tokens lidos;
  - definição do escore;
  - lista fechada de configurações candidatas (sugiro no máximo 6 para o LLM);
  - forma da regra de abstenção;
  - critério de seleção e de desempate (em empate dentro do IC, a mais barata);
  - denominador do risco de FP;
  - uso único do teste.
- **Deixar para o desenvolvimento:** o limiar, a escolha dentro da lista fechada e o Platt scaling.
- **Contra ajuste excessivo:**
  - separar por código de barras, não por par, para a mesma descrição não aparecer em desenvolvimento e teste;
  - dividir o desenvolvimento em duas partes (uma para escolher, outra olhada uma única vez para confirmar);
  - usar bootstrap para as diferenças.
- **Tamanho do teste:** para afirmar risco de FP abaixo de 1% com zero FP, são necessários cerca de 300 pares aceitos (limite unilateral de 95%).

**5. Justiça na comparação.** O argumento mais forte é que similaridade textual e cosseno de embeddings já são simétricos. As duas chamadas dão ao LLM uma propriedade que os outros têm de graça. Para equilibrar:

- Adote uma regra única: todo método deve ser invariante à ordem. Verifique se as features da regressão logística são simétricas.
- Reporte o LLM de uma chamada como ablação.
- Reporte custo por par para os quatro métodos.

A injustiça maior, na minha opinião, não são as chamadas. É o número de configurações testadas por método no desenvolvimento, e isso se iguala com um orçamento de configurações pré-declarado.

## Plano para 3 a 4 horas

1. **Conjunto de desenvolvimento v0 (1 h).** 300 a 400 pares de Alagoas com rótulo por código de barras e negativos difíceis estratificados. Sem ele, nada abaixo é interpretável. Se a coleta ainda não existe, gaste as 4 horas aqui.
2. **Auditoria da leitura (30 min).** Massa absoluta em {0,1}, divergência entre primeiro token e texto gerado, e repetição do mesmo par para checar determinismo com batch.
3. **Rodada principal (45 min).** 7B em 4 bits, 3B em float16 e 3B em 4 bits, nas duas ordens. Saídas: taxa de inversão com IC, direção média, curvas risco–cobertura para A×B, B×A, média e mínimo, e o efeito isolado da quantização.
4. **Variante de rótulos (30 min).** Rótulos invertidos ou "sim/não", para medir o prior de token.
5. **Few-shot (30 a 40 min, se sobrar).** Quatro demonstrações com negativos difíceis, cada par mostrado nas duas ordens.
6. **Outra família de modelo (opcional).** Generaliza o achado, mas não muda a decisão.

Normalização do escore não vale tempo agora: transformação monótona não altera a curva risco–cobertura.

## Referências (todas abertas)

- [Wang et al., "Large Language Models are not Fair Evaluators"](https://arxiv.org/abs/2305.17926v2). Mostra que basta trocar a ordem das respostas para manipular o veredito do avaliador; a correção proposta, Balanced Position Calibration, combina os resultados obtidos em ordens diferentes. É o precedente mais direto para a sua média. A página que abri não detalha a fórmula de agregação.
- [Zheng et al., "LLMs Are Not Robust Multiple Choice Selectors"](https://arxiv.org/pdf/2309.03882) (ICLR 2024). Separa viés de token (prior sobre os IDs das opções, a causa principal) de viés de posição, que é menos regular e varia com modelo e tarefa. Sustenta a ressalva de que trocar A e B não cancela o prior de "0"/"1".
- [Qin et al., "Pairwise Ranking Prompting"](https://arxiv.org/pdf/2306.17563). Consulta cada par nas duas ordens e, havendo conflito, registra empate. É o precedente para tratar discordância como dúvida.
- [Zeng et al., "LLM-RankFusion"](https://arxiv.org/html/2406.00231v2). Dá nome ao fenômeno (order inconsistency) e o mede pelos logits das duas permutações; o few-shot deles exibe o mesmo par nas duas ordens. Inspira o teste 5.
- [Wang et al., "Match, Compare, or Select?"](https://arxiv.org/pdf/2405.16884) (COLING 2025). Em entity matching, a estratégia de comparação repete cada par com a ordem invertida, justificada pela sensibilidade do LLM à ordem do prompt.
- [Steiner, Peeters e Bizer, "Entity Matching using Decision Models"](https://arxiv.org/pdf/2610.34626) (out/2026). No teste de troca de registros, entre 0,8% e 3,7% das decisões mudaram, e a cascata aplica a regra de Chow para adiar os pares incertos. É o trabalho mais próximo do seu desenho e dá uma taxa de inversão de referência em pares não escolhidos a dedo.
- [Peeters, Steiner e Bizer, "Entity Matching using Large Language Models"](https://arxiv.org/abs/2310.11244v4) (EDBT 2025). Não encontram um prompt melhor em geral; o ajuste é por combinação de modelo e dataset. Justifica a lista fechada de prompts no pré-registro.
- [Wang et al., "Look at the Text"](https://arxiv.org/pdf/2404.08382). Quando primeiro token e resposta em texto divergem, o texto resiste melhor a perturbações da pergunta. Justifica a auditoria do passo 2.
- [Zhao et al., "Calibrate Before Use"](https://proceedings.mlr.press/v139/zhao21c.html) (ICML 2021). Uma entrada sem conteúdo, como "N/A", serve para estimar a inclinação do modelo por cada resposta. É uma forma barata de medir o prior de "0".
- [Geifman e El-Yaniv, "Selective Classification for Deep Neural Networks"](https://arxiv.org/pdf/1705.08500) (NeurIPS 2017). O limiar sai de uma amostra rotulada separada do teste, com limite por cauda binomial. É a base formal do seu Clopper-Pearson com limiar fixado antes do teste.
- [Shi et al., "Judging the Judges"](https://arxiv.org/html/2406.07791v9). Distingue estabilidade sob repetição de consistência sob troca de posição. Traz métricas prontas para reportar a sensibilidade à ordem. Li só a primeira metade da página.
- [Kamsteeg et al., "Confidence Calibration in LLM-Based Entity Matching"](https://aclanthology.org/2025.uncertainlp-main.12/) (UncertaiNLP 2025). Temperature scaling corta o ECE em até 23,83%, mas o modelo estudado é um RoBERTa modificado, não um LLM generativo. Cite com essa ressalva.