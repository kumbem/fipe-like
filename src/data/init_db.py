import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fipe.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        conn.commit()
    finally:
        conn.close()

    print("Banco criado com sucesso!")


if __name__ == "__main__":
    main()
