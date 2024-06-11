# Projeto Num-Query
## Objetivo
Testar capacidades de descoberta e análise rápida de dados estruturados por meio de prompts de LLM.

## Funcionalidades
- [x] **Prompt livre**
- [x] **Validação de SQL**
- [x] **Dados de glossário**
- [x] **Dados de schema**
- [x] **Dados fundacionais**
- [ ] Dados auxiliares
- [ ] Sugestão de prompt
- [ ] Tags de recorrência
- [ ] Caching
- [ ] Transparência de SQL

## Funcionamento
O diagrama abaixo demonstra os elementos de back-end por trás da interface de prompt web.
Uma cadeia de LLMs formada por um langchain une prompts e ações que retornam dados de glossário e metadados de schema para criar um contexto e restringir os resultados baseado em conhecimento externo enquanto diminuem a possibilidade de halucinações. A criação do contexto é seguida da formação de um SQL validado na própria engine do BigQuery antes de acessar o conteúdo específico da tabela, ou tabelas no caso de relacionamentos, para retornar um valor isolado na resposta da requisição HTTP.

![HLD do Projeto](https://storage.googleapis.com/qa-agent-misc/HLD.png)
