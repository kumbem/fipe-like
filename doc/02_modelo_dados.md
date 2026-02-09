Modelo de Dados (atualizado p/ “busca em pesquisa_preco”)
1) Entidades principais

Catálogo: Marca → Modelo → Versão

Coleta: Loja, Região, Pesquisador, Pesquisa de preço

Consulta: resultado calculado (não necessariamente persistido) + log opcional

2) Tabelas (mínimo + completo)
marca

id (PK)

nome (unique)

modelo

id (PK)

marca_id (FK → marca.id)

nome

unique (marca_id, nome)

versao

id (PK)

modelo_id (FK → modelo.id)

nome

ano_modelo

unique (modelo_id, nome, ano_modelo)

regiao (projeto)

id (PK)

nome

cidade

latitude_centro (opcional)

longitude_centro (opcional)

loja (projeto)

id (PK)

regiao_id (FK → regiao.id)

nome

endereco

status_aprovacao (pendente/aprovado)

pesquisador (projeto)

id (PK)

nome

regiao_id (FK → regiao.id)

pesquisa_preco (captura bruta) ✅ (base para consulta)

id (PK)

loja_id (FK → loja.id) (pode ser opcional no MVP)

pesquisador_id (FK → pesquisador.id) (opcional no MVP)

versao_id (FK → versao.id)

data_coleta (datetime)

preco (decimal)

observacao (texto opcional)

consulta_log (opcional)

id (PK)

dt (datetime)

mes_ref (int)

ano_ref (int)

versao_id (FK)

mes_usado (int)

ano_usado (int)

preco_resultado (decimal)

3) Observação importante (para justificar no relatório)

O preço “FIPE-like” não precisa estar salvo em cotacao_mensal: ele pode ser derivado de pesquisa_preco no momento da consulta.

Em um sistema real, poderia existir um batch que consolida e grava cotação mensal, mas aqui será apenas projetado.