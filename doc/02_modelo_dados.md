# Modelo de Dados - FIPE-LIKE (SQLite)

## 1. Objetivo e escopo

Este documento descreve o modelo fisico de dados usado pelo sistema FIPE-LIKE.
O objetivo do modelo e suportar dois fluxos:

1. Catalogo e consulta de preco por cadeia `marca -> modelo -> versao -> cotacao`.
2. Registro de auditoria das consultas em `consulta_log`.

## 2. Estrutura relacional (ERD textual)

Relacionamentos principais:

- `marca (1) -> (N) modelo`
- `modelo (1) -> (N) versao`
- `versao (1) -> (N) cotacao`
- `marca/modelo/versao (1) -> (N) consulta_log`

Decisao de modelagem:

- `consulta_log` referencia entidades por ID (FK), garantindo rastreabilidade consistente com o catalogo.

## 3. Dicionario de dados

### 3.1 Tabela `marca`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `nome` | `TEXT` | `NOT NULL`, `UNIQUE` |

### 3.2 Tabela `modelo`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `marca_id` | `INTEGER` | `NOT NULL`, FK -> `marca(id)`, `ON DELETE RESTRICT` |
| `nome` | `TEXT` | `NOT NULL` |

Restricao adicional: `UNIQUE (marca_id, nome)`

### 3.3 Tabela `versao`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `modelo_id` | `INTEGER` | `NOT NULL`, FK -> `modelo(id)`, `ON DELETE RESTRICT` |
| `nome` | `TEXT` | `NOT NULL` |

Restricao adicional: `UNIQUE (modelo_id, nome)`

### 3.4 Tabela `cotacao`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `versao_id` | `INTEGER` | `NOT NULL`, FK -> `versao(id)`, `ON DELETE RESTRICT` |
| `ano` | `INTEGER` | `NOT NULL`, `CHECK (ano BETWEEN 1900 AND 2100)` |
| `mes` | `INTEGER` | `NOT NULL`, `CHECK (mes BETWEEN 1 AND 12)` |
| `preco` | `REAL` | `NOT NULL`, `CHECK (preco >= 0)` |

Restricao adicional: `UNIQUE (versao_id, ano, mes)`

### 3.5 Tabela `consulta_log`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `data_hora` | `TEXT` | `NOT NULL`, default `datetime('now')` |
| `marca_id` | `INTEGER` | `NOT NULL`, FK -> `marca(id)`, `ON DELETE RESTRICT` |
| `modelo_id` | `INTEGER` | `NOT NULL`, FK -> `modelo(id)`, `ON DELETE RESTRICT` |
| `versao_id` | `INTEGER` | `NOT NULL`, FK -> `versao(id)`, `ON DELETE RESTRICT` |
| `mes` | `INTEGER` | `NOT NULL`, `CHECK (mes BETWEEN 1 AND 12)` |
| `ano` | `INTEGER` | `NOT NULL`, `CHECK (ano BETWEEN 1900 AND 2100)` |

## 4. Regras de integridade

A integridade e garantida por:

1. FKs no `schema.sql` com `ON DELETE RESTRICT`.
2. Ativacao de FK por conexao em runtime com `PRAGMA foreign_keys = ON` (`src/db.py`).

Invariantes esperadas:

- Nao existe `modelo` sem `marca` valida.
- Nao existe `versao` sem `modelo` valido.
- Nao existe `cotacao` sem `versao` valida.
- Nao existe `consulta_log` com IDs orfaos.
- Nao existe duplicidade de cotacao para a mesma chave funcional (`versao_id`, `ano`, `mes`).

## 5. Indices e impacto em consulta

Indices definidos:

- `idx_modelo_marca_id` em `modelo(marca_id)`
- `idx_versao_modelo_id` em `versao(modelo_id)`
- `idx_cotacao_versao` em `cotacao(versao_id)`
- `idx_cotacao_periodo` em `cotacao(ano, mes)`
- `idx_log_data_hora` em `consulta_log(data_hora)`
- `idx_log_periodo` em `consulta_log(ano, mes)`
- `idx_log_marca_id` em `consulta_log(marca_id)`
- `idx_log_modelo_id` em `consulta_log(modelo_id)`
- `idx_log_versao_id` em `consulta_log(versao_id)`

Observacao tecnica:

- O `UNIQUE (versao_id, ano, mes)` em `cotacao` tambem gera indice util para busca por chave completa.

## 6. Operacao e evolucao

- Estrutura do banco: `src/data/schema.sql` via `src/data/init_db.py`.
- Popular dados de exemplo: `src/data/seed_db.py`.
- Evolucao do schema deve ser sincronizada com:
  - Repositorio (`src/repo_fipe.py`)
  - Testes (`src/test_repo.py`)
  - Documentacao de dados (`doc/02_modelo_dados.md`)

## Chave Funcional do Sistema

A entidade `cotacao` representa a cotacao mensal oficial de uma versao de veiculo.

A chave funcional do dominio e composta por:

`(versao_id, ano, mes)`

Isso significa que:

- Para cada versao de veiculo
- Em um determinado mes
- Em um determinado ano
- Deve existir no maximo uma unica cotacao registrada.

Essa regra de negocio e garantida no modelo fisico atraves da constraint:

`UNIQUE (versao_id, ano, mes)`

Essa decisao assegura:

- Consistencia temporal
- Reprodutibilidade das consultas
- Impossibilidade de duplicacao de cotacoes mensais

