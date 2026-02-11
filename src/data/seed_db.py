import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fipe.db"


def get_or_create_marca(cur: sqlite3.Cursor, nome: str) -> int:
    cur.execute("INSERT OR IGNORE INTO marca(nome) VALUES (?);", (nome,))
    cur.execute("SELECT id FROM marca WHERE nome = ?;", (nome,))
    return cur.fetchone()[0]


def get_or_create_modelo(cur: sqlite3.Cursor, marca_id: int, nome: str) -> int:
    cur.execute(
        "INSERT OR IGNORE INTO modelo(marca_id, nome) VALUES (?, ?);",
        (marca_id, nome),
    )
    cur.execute(
        "SELECT id FROM modelo WHERE marca_id = ? AND nome = ?;",
        (marca_id, nome),
    )
    return cur.fetchone()[0]


def get_or_create_versao(cur: sqlite3.Cursor, modelo_id: int, nome: str) -> int:
    cur.execute(
        "INSERT OR IGNORE INTO versao(modelo_id, nome) VALUES (?, ?);",
        (modelo_id, nome),
    )
    cur.execute(
        "SELECT id FROM versao WHERE modelo_id = ? AND nome = ?;",
        (modelo_id, nome),
    )
    return cur.fetchone()[0]


def insert_cotacao(
    cur: sqlite3.Cursor, versao_id: int, ano: int, mes: int, preco: float
) -> None:
    cur.execute(
        """
        INSERT OR IGNORE INTO cotacao(versao_id, ano, mes, preco)
        VALUES (?, ?, ?, ?);
        """,
        (versao_id, ano, mes, preco),
    )


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco nao encontrado em: {DB_PATH}. Rode antes: python src/data/init_db.py"
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        dados = {
            "Fiat": {
                "Argo": {
                    "1.0": [(2025, 1, 78000.0), (2025, 2, 79000.0)],
                    "Trekking 1.3": [(2025, 1, 94000.0), (2025, 2, 95200.0)],
                },
                "Cronos": {
                    "Drive 1.3": [(2025, 1, 90500.0), (2025, 2, 91500.0)],
                },
            },
            "Volkswagen": {
                "Polo": {
                    "TSI": [(2025, 1, 106000.0), (2025, 2, 107500.0)],
                },
                "Nivus": {
                    "Comfortline": [(2025, 1, 131000.0), (2025, 2, 132300.0)],
                },
            },
            "Chevrolet": {
                "Onix": {
                    "LT 1.0": [(2025, 1, 87200.0), (2025, 2, 88000.0)],
                },
            },
        }

        for marca_nome, modelos in dados.items():
            marca_id = get_or_create_marca(cur, marca_nome)
            for modelo_nome, versoes in modelos.items():
                modelo_id = get_or_create_modelo(cur, marca_id, modelo_nome)
                for versao_nome, cotacoes in versoes.items():
                    versao_id = get_or_create_versao(cur, modelo_id, versao_nome)
                    for ano, mes, preco in cotacoes:
                        insert_cotacao(cur, versao_id, ano, mes, preco)

        conn.commit()
    finally:
        conn.close()

    print("Seed aplicada com sucesso.")


if __name__ == "__main__":
    main()
