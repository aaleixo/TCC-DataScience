# TCC — Confiabilidade na normalização de produtos de cupons fiscais

Trabalho de conclusão do curso de Data Science (Unicamp), de Alessandra Aleixo Ferreira, sob orientação do Prof. Rangel Arthur.

**Pergunta:** como diferentes métodos de correspondência de descrições de produtos em cupons fiscais se comportam em acurácia e confiabilidade, e em que medida a abstenção baseada em confiança reduz associações incorretas (erro silencioso)?

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `coleta/` | Script usado para coletar, em pequena escala, descrições e códigos de barras no site público do Economiza Alagoas (23/11/2026) |
| `scripts/` | `montar_pares.py` (monta os pares do conjunto de desenvolvimento, semente 20261123) e `teste_llm_local.py` (teste do LLM via llama.cpp no notebook) |
| `notebooks/` | Testes técnicos do LLM no Google Colab: v1 (viabilidade), v2 (três formas de escore), v3 (auditoria sem rótulo), v4 (7B em float16 na L4) |
| `dados/` | Coleta bruta (`coleta_economiza_al_2026-11-23.tsv`) e o conjunto de desenvolvimento v0 (`dados/dev_v0/`) |
| `resultados/` | Resultados dos testes técnicos |
| `docs/proposta/` | Proposta v1 (enviada ao orientador) e rascunho atual da v2 |
| `docs/revisoes/` | Revisões adversariais da proposta e dos testes |
| `docs/acompanhamento.md` | Linha do tempo, decisões fechadas e pendências |

## Reproduzir o conjunto de desenvolvimento v0

```bash
python scripts/montar_pares.py dados/dev_v0/dev_v0 dados/coleta_economiza_al_2026-11-23.tsv
```

## Regras do estudo

- Os pares de `dados/dev_v0/` são de **desenvolvimento** e nunca entram no conjunto de teste.
- O pré-registro (hipóteses, métricas, configurações candidatas e grade de limiares) será registrado em commit datado antes de abrir o teste.
- Os rótulos da base de referência são feitos pela autora, não por um modelo.

## Origem dos dados

Os dados vêm do Economiza Alagoas, plataforma de preços da Secretaria da Fazenda de Alagoas, a partir de documentos fiscais eletrônicos. Não há dados de pessoas. O acesso à API pública foi solicitado à Sefaz-AL em 22/11/2026.
