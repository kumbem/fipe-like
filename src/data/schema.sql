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

-- Cotacao (preco medio por mes/ano para uma versao)
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
-- Logs (consulta)
-- =========================

CREATE TABLE IF NOT EXISTS consulta_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  data_hora     TEXT NOT NULL DEFAULT (datetime('now')),
  marca_id      INTEGER NOT NULL,
  modelo_id     INTEGER NOT NULL,
  versao_id     INTEGER NOT NULL,
  mes           INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
  ano           INTEGER NOT NULL CHECK (ano BETWEEN 1900 AND 2100),
  FOREIGN KEY (marca_id) REFERENCES marca(id) ON DELETE RESTRICT,
  FOREIGN KEY (modelo_id) REFERENCES modelo(id) ON DELETE RESTRICT,
  FOREIGN KEY (versao_id) REFERENCES versao(id) ON DELETE RESTRICT
);

-- =========================
-- Indices
-- =========================

CREATE INDEX IF NOT EXISTS idx_modelo_marca_id      ON modelo(marca_id);
CREATE INDEX IF NOT EXISTS idx_versao_modelo_id     ON versao(modelo_id);

CREATE INDEX IF NOT EXISTS idx_cotacao_versao       ON cotacao(versao_id);
CREATE INDEX IF NOT EXISTS idx_cotacao_periodo      ON cotacao(ano, mes);

CREATE INDEX IF NOT EXISTS idx_log_data_hora        ON consulta_log(data_hora);
CREATE INDEX IF NOT EXISTS idx_log_periodo          ON consulta_log(ano, mes);
CREATE INDEX IF NOT EXISTS idx_log_marca_id         ON consulta_log(marca_id);
CREATE INDEX IF NOT EXISTS idx_log_modelo_id        ON consulta_log(modelo_id);
CREATE INDEX IF NOT EXISTS idx_log_versao_id        ON consulta_log(versao_id);
