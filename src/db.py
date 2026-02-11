import sqlite3
from pathlib import Path

# Caminho do banco: src/data/fipe.db
DB_PATH = Path(__file__).resolve().parent / "data" / "fipe.db"


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma NOVA conexao SQLite para cada chamada.

    Decisoes de projeto:
    - check_same_thread=False: Streamlit pode executar callbacks/requests em
      threads diferentes; essa flag evita erro de ownership da conexao.
    - Nao usar singleton/global connection: conexao compartilhada tende a
      causar contenção e efeitos colaterais entre sessoes/threads.
      O padrao adotado e abrir por uso e fechar no repositorio com try/finally.
    - PRAGMA foreign_keys=ON: garante integridade referencial em runtime para
      cada conexao aberta.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco nao encontrado em: {DB_PATH}. "
            f"Crie com: python src/data/init_db.py"
        )

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
