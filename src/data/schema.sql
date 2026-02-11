-- src/data/schema.sql
PRAGMA foreign_keys = ON;

-- =========================
-- Tabelas principais (FIPE)
-- =========================

CREATE TABLE IF NOT EXISTS marca (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  nome          TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS modelo (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  marca_id      INTEGER NOT NULL,
  nome          TEXT NOT NULL,
  UNIQUE (marca_id, nome),
  FOREIGN KEY (marca_id) REFERENCES marca(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS versao (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  modelo_id     INTEGER NOT NULL,
  nome          TEXT NOT NULL,
  UNIQUE (modelo_id, nome),
  FOREIGN KEY (modelo_id) REFERENCES modelo(id) ON DELETE RESTRICT
);

-- Cotação (preço médio por mês/ano para uma versão)
CREATE TABLE IF NOT EXISTS cotacao (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  versao_id     INTEGER NOT NULL,
  ano           INTEGER NOT NULL CHECK (ano BETWEEN 1900 AND 2100),
  mes           INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
  preco         REAL NOT NULL CHECK (preco >= 0),

  UNIQUE (versao_id, ano, mes),
  FOREIGN KEY (versao_id) REFERENCES versao(id) ON DELETE RESTRICT
);

-- =========================
-- Logs (STORY 4)
-- =========================

CREATE TABLE IF NOT EXISTS consulta_log (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at        TEXT NOT NULL DEFAULT (datetime('now')),

  ano               INTEGER NOT NULL CHECK (ano BETWEEN 1900 AND 2100),
  mes               INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),

  marca_nome        TEXT NOT NULL,
  modelo_nome       TEXT NOT NULL,
  versao_nome       TEXT NOT NULL,

  -- opcional: guardar o preço retornado (ajuda auditoria de resultado)
  preco_retornado   REAL
);

-- =========================
-- Índices
-- =========================

CREATE INDEX IF NOT EXISTS idx_modelo_marca_id      ON modelo(marca_id);
CREATE INDEX IF NOT EXISTS idx_versao_modelo_id     ON versao(modelo_id);

CREATE INDEX IF NOT EXISTS idx_cotacao_versao       ON cotacao(versao_id);
CREATE INDEX IF NOT EXISTS idx_cotacao_periodo      ON cotacao(ano, mes);

CREATE INDEX IF NOT EXISTS idx_log_created_at       ON consulta_log(created_at);
CREATE INDEX IF NOT EXISTS idx_log_periodo          ON consulta_log(ano, mes);
