import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "fipe.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        print("Tabelas criadas:")
        for t in tables:
            print("-", t[0])
    finally:
        conn.close()


if __name__ == "__main__":
    main()
