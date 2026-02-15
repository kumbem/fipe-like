# ADR-003: Fallback automatico para ultimo mes com cotacao

## Status
Aceita

## Contexto
A base de cotacoes pode estar incompleta para determinados periodos.
Sem fallback, a consulta retorna ausencia de cotacao mesmo quando existe historico anterior valido para a mesma versao.
Isso reduz robustez e piora experiencia de uso.

## Decisao
Ao consultar `versao_id`, `mes` e `ano`, o sistema deve:

1. Tentar cotacao exata do periodo selecionado.
2. Se nao existir, usar automaticamente o ultimo periodo anterior disponivel para a mesma versao.
3. Se nao houver nenhum periodo anterior, retornar ausencia de cotacao.

Implementacao tecnica:
- Ordenar cotacoes por `ano DESC, mes DESC`.
- Filtrar por periodos `<=` ao solicitado.
- Selecionar apenas `LIMIT 1`.

## Consequencias
Positivas:
- A consulta fica resiliente a lacunas mensais na carga de dados.
- O usuario recebe um preco util em mais cenarios.

Trade-offs:
- O preco exibido pode ser de periodo anterior ao solicitado.
- A interface deve informar explicitamente quando fallback for aplicado.

## Alternativas consideradas
1. Retornar `None` sempre que o periodo exato faltar.
2. Buscar periodo posterior mais proximo.
3. Usar media dos ultimos periodos disponiveis.

As alternativas 2 e 3 foram descartadas por alterarem semanticamente o conceito de "preco do periodo consultado".
O fallback para periodo anterior preserva interpretacao temporal conservadora.
