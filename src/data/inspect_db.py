from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent / "fipe.db"


def main():
    print(f"Inspecting database: {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cur.fetchall()]

        if not tables:
            print("No user tables found.")
            return

        for t in tables:
            print(f"Table: {t}")
            cur.execute(f"PRAGMA table_info({t});")
            cols = [r[1] for r in cur.fetchall()]
            print("Columns:", ", ".join(cols))
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print("Rows:", cnt)
            cur.execute(f"SELECT * FROM {t} LIMIT 10")
            rows = cur.fetchall()
            if rows:
                for r in rows:
                    print(dict(r))
            else:
                print("(no rows)")
            print()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
