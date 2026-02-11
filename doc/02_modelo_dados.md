# Modelo de Dados - FIPE-LIKE (SQLite)

## 1. Visao geral e objetivos

O modelo de dados do FIPE-LIKE foi desenhado para dois objetivos principais:

1. Suportar consulta de preco medio por veiculo (cadeia `marca -> modelo -> versao -> cotacao`).
2. Registrar telemetria das consultas realizadas (tabela `consulta_log`).

Em termos funcionais, o catalogo de veiculos fica normalizado em tres niveis (`marca`, `modelo`, `versao`) e os valores mensais/anuais ficam em `cotacao`.

## 2. ERD textual

Fluxo principal de dominio:

`marca (1) -> (N) modelo (1) -> (N) versao (1) -> (N) cotacao`

Telemetria (desacoplada por design):

`consulta_log` registra os parametros/resultados da consulta para auditoria e observabilidade, sem FK obrigatoria para as tabelas de catalogo.

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

Restricoes adicionais:

- `UNIQUE (marca_id, nome)`

### 3.3 Tabela `versao`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `modelo_id` | `INTEGER` | `NOT NULL`, FK -> `modelo(id)`, `ON DELETE RESTRICT` |
| `nome` | `TEXT` | `NOT NULL` |

Restricoes adicionais:

- `UNIQUE (modelo_id, nome)`

### 3.4 Tabela `cotacao`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `versao_id` | `INTEGER` | `NOT NULL`, FK -> `versao(id)`, `ON DELETE RESTRICT` |
| `ano` | `INTEGER` | `NOT NULL`, `CHECK (ano BETWEEN 1900 AND 2100)` |
| `mes` | `INTEGER` | `NOT NULL`, `CHECK (mes BETWEEN 1 AND 12)` |
| `preco` | `REAL` | `NOT NULL`, `CHECK (preco >= 0)` |

Restricoes adicionais:

- `UNIQUE (versao_id, ano, mes)`

Observacao:

- No schema atual, a coluna de valor e `preco`.
- Caso o projeto migre para `preco_medio`, a migracao deve atualizar queries/repositorio e testes em conjunto.

### 3.5 Tabela `consulta_log`

| Coluna | Tipo | Regras |
|---|---|---|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `created_at` | `TEXT` | `NOT NULL`, default `datetime('now')` |
| `ano` | `INTEGER` | `NOT NULL`, `CHECK (ano BETWEEN 1900 AND 2100)` |
| `mes` | `INTEGER` | `NOT NULL`, `CHECK (mes BETWEEN 1 AND 12)` |
| `marca_nome` | `TEXT` | `NOT NULL` |
| `modelo_nome` | `TEXT` | `NOT NULL` |
| `versao_nome` | `TEXT` | `NOT NULL` |
| `preco_retornado` | `REAL` | opcional (`NULL` permitido) |

## 4. Integridade referencial

A integridade referencial e aplicada em dois niveis:

1. Definicao de FK no `schema.sql` com `ON DELETE RESTRICT`.
2. Ativacao por conexao em runtime: `PRAGMA foreign_keys = ON` em `src/db.py`.

Comportamento esperado:

- Nao e permitido inserir `modelo` com `marca_id` inexistente.
- Nao e permitido inserir `versao` com `modelo_id` inexistente.
- Nao e permitido inserir `cotacao` com `versao_id` inexistente.
- Nao e permitido deletar `marca` com `modelo` vinculado (mesmo principio para os demais niveis da cadeia).

## 5. Indices

Indices ja existentes no schema:

- `idx_modelo_marca_id` em `modelo(marca_id)`
- `idx_versao_modelo_id` em `versao(modelo_id)`
- `idx_cotacao_versao` em `cotacao(versao_id)`
- `idx_cotacao_periodo` em `cotacao(ano, mes)`
- `idx_log_created_at` em `consulta_log(created_at)`
- `idx_log_periodo` em `consulta_log(ano, mes)`

Indices recomendados (evolucao):

- Busca textual por nome de marca/modelo/versao:
  - `marca(nome)` (ja coberto por `UNIQUE`, mas pode ser analisado no plano de consultas)
  - `modelo(nome)`
  - `versao(nome)`
- Consulta direta de cotacao por chave funcional completa:
  - `cotacao(versao_id, mes, ano)`

Observacao: no schema atual existe `UNIQUE (versao_id, ano, mes)`, que ja cria indice util para consultas com esses tres campos.

## 6. Seed e estado inicial do banco

- O banco e criado com estrutura via `src/data/init_db.py` + `src/data/schema.sql`.
- O estado inicial apos criacao e vazio (sem dados de dominio).
- A populacao de dados de exemplo e feita por `src/data/seed_db.py`.
- O seed e idempotente (usa `INSERT OR IGNORE`), permitindo execucoes repetidas sem duplicar registros logicos.

## 7. Versionamento e evolucao do schema

Recomendacoes para evoluir `schema.sql` com seguranca:

1. Nunca renomear/remover coluna em producao sem script de migracao explicito.
2. Versionar mudancas por arquivo de migracao incremental (ex.: `migrations/001_*.sql`, `002_*.sql`).
3. Atualizar em conjunto:
   - schema/migracao,
   - camada de repositorio (`src/repo_fipe.py`),
   - testes (`src/test_repo.py` e testes de integridade).
4. Registrar no changelog de dados:
   - data,
   - motivacao,
   - impacto em retrocompatibilidade,
   - plano de rollback.

Isso reduz risco de divergencia entre estrutura do banco, codigo e documentacao.
