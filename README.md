# Deep FIPE Seek

Sistema academico de modelagem, governanca e consulta publica de precos medios de veiculos, inspirado na Tabela FIPE.

---

## Visao Geral

O Deep FIPE Seek foi projetado para simular o ciclo completo de vida da formacao de precos de veiculos:

1. Cadastro de dados mestres (Marca, Modelo, Versao)
2. Governanca regional de coleta
3. Coleta de dados brutos em campo
4. Consolidacao mensal via processamento batch
5. Consulta publica de precos medios

Nesta entrega, foi implementado o **MVP da Consulta Publica**, mantendo o modelo completo projetado conceitualmente.

---

## Arquitetura

O sistema foi estruturado em cinco dominios principais:

### 1) Master Data
- Marca
- Modelo
- Versao

### 2) Governanca
- Regiao
- Coordenador
- Pesquisador
- Loja
- PlanoPesquisa
- PlanoPesquisaItem

### 3) Coleta de Dados
- ColetaPreco (dados brutos)

### 4) Processamento Mensal
- BatchExecucao
- CotacaoMensal

### 5) Consulta Publica (MVP Implementado)
- ConsultaLog

---

## Estrutura do Projeto

```text
fipe-like/
  src/
    app.py
    repo_fipe.py
    db.py
    test_repo.py
    data/
      schema.sql
      init_db.py
      seed_db.py
      check_db.py
      check_conn.py
  doc/
    01_escopo.md
    02_modelo_dados.md
    03_tdd_design.md
    adr/
      ADR-003-fallback-automatico-cotacao.md
  README.md
```

---

## Decisoes Arquiteturais

- Uso de SQLite para simplificacao academica
- Integridade referencial explicitamente ativada (`PRAGMA foreign_keys = ON`)
- Repository Pattern para isolamento de queries
- Frontend sem SQL
- Log resiliente a falhas
- Modelagem completa mesmo com implementacao parcial

---

## Como Executar

### 1) Criar banco

```bash
python src/data/init_db.py
```

### 2) Popular dados (seed)

```bash
python src/data/seed_db.py
```

### 3) Validar regra de repositorio

```bash
python src/test_repo.py
```

### 4) Executar a interface

```bash
streamlit run src/app.py
```
