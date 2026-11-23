Li a proposta: ela já resolve parte do que apontei, mas entra em conflito com a regra que você quer adotar para o LLM em quatro pontos. O principal é que **a escolha entre média, mínimo ou ordem única não precisa ser decidida antes do pré-registro**. Pelo seu próprio desenho, prompts e hiperparâmetros são decisões do desenvolvimento; o pré-registro só precisa delimitar o espaço permitido.

## O que retiro ou ajusto da revisão anterior

- **Denominador do risco de FP:** já está definido (FPs entre os pares aceitos como mesmo produto).
- **Divisão por código de barras:** a sua, por marca × categoria, é mais rígida e melhor.
- **Custo por par:** já previsto como linha de custo e latência.
- **Tamanho do teste:** meu "cerca de 300 para 1%" era unilateral. Na sua convenção bilateral, zero erro em 300 dá 1,2%, como você escreveu, e X fica em 3% a 5%.
- **Conjunto de desenvolvimento de Alagoas em 1 hora:** inviável agora. O token ainda está sendo pedido e a base só fica pronta em 10–13/12. O plano revisado está no fim.

## Conflitos entre o teste preliminar e a proposta

| Ponto | Gravidade | Conflito | O que fazer |
|---|---|---|---|
| "Leituras repetidas" estão fora do escopo | Crítica | Duas ordens são duas leituras do LLM por par. Um avaliador pode ler isso como violação do escopo declarado. | Restringir o termo a amostragem estocástica e declarar a simetrização como parte determinística do método. |
| Discordância de sinal como variável auxiliar | Crítica | A proposta aplica a mesma política a todos: dois limiares sobre uma probabilidade. Uma segunda variável dá ao LLM uma regra bidimensional que os outros não têm. | Manter um escore escalar único (média ou mínimo já embutem a discordância). A discordância entra só como análise exploratória. |
| Token lido | Importante | A proposta define o escore como probabilidade do token "sim"; o teste leu "1" e "0". | Escolher um e alinhar o texto. A variante sim/não que sugeri deixa de ser opcional. |
| Pares não decidíveis | Importante | A proposta os inclui na avaliação principal; a estatística "16,3 vs 1,5" os excluiu. | Recalcular com os 15 pares, como já apontei. |

O descarte do prompt de três opções fica coerente com a proposta: a opção "informação insuficiente" é confiança declarada pelo LLM, que já está fora do escopo. Essa é uma justificativa melhor que "instável entre modelos".

## Problemas novos na proposta que tocam o pré-registro

- **Clopper-Pearson com pares correlacionados (importante).** A proposta reconhece a correlação dentro do grupo, mas o critério de H2 é um IC binomial sobre pares. Com agrupamento, os 95% nominais ficam otimistas. Fixe no pré-registro o limite de pares aceitos por grupo ou o ajuste usado.
- **Ponderação por estrato (importante).** As métricas são "ponderadas para a população", mas Clopper-Pearson vale para contagem não ponderada. Diga qual das duas H2 usa.
- **Escolha do limiar alto (importante).** Escolher "o mais permissivo cujo limite fica abaixo de X" varrendo vários limiares é teste múltiplo. Geifman e El-Yaniv corrigem dividindo δ pelo número de limiares testados. Sem correção, o limiar sai otimista e H2 pode falhar no teste por esse motivo. Não abri o Learn then Test, então confira como ele trata isso.
- **Contaminação pelos 15 pares (menor).** Você ajustou a regra olhando para eles. Como a divisão é por marca × categoria, force esses grupos (Royal, Moça, Crystal, Xandó, Piracanjuba etc.) para o lado do desenvolvimento.

## Plano revisado para as 3 a 4 horas

Taxa de inversão, direção do efeito de ordem, massa no primeiro token e efeito da quantização não precisam de rótulo. Dá para medi-los agora em pares não rotulados dos seus cupons de SP.

1. **Auditoria da leitura (45 min).** Massa absoluta nos tokens de resposta, divergência entre primeiro token e texto gerado, determinismo com batch.
2. **Rótulos (45 min).** "sim/não" contra "1/0", nas duas ordens.
3. **Quantização (30 min).** 3B em 4 bits contra 3B em float16.
4. **Sensibilidade à ordem (45 min).** Taxa de inversão e direção média em algumas centenas de pares não rotulados, para 7B e 3B.

A comparação entre A×B, B×A, média e mínimo precisa de rótulo e fica para o desenvolvimento, depois de 20/12.

## O que escrever no pré-registro sobre o LLM

- Lista fechada de configurações candidatas (modelo, quantização, prompt, token, operador de agregação).
- Critério de escolha no desenvolvimento e regra de desempate.
- Escore escalar único, calibrado pela mesma logística de uma variável dos outros métodos.
- Exigência de invariância à ordem para os quatro métodos.

Das referências da proposta, abri Peeters, Steiner e Bizer, Kamsteeg et al. e Geifman e El-Yaniv. Kamsteeg estuda um RoBERTa, não um LLM generativo. As brasileiras, Traub et al. e o Learn then Test eu não conferi.