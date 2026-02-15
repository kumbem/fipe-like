import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "fipe.db"
ANOS_BASE = list(range(2016, 2026))


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


def gerar_cotacoes(preco_base: float) -> list[tuple[int, int, float]]:
    cotacoes: list[tuple[int, int, float]] = []
    for idx, ano in enumerate(ANOS_BASE):
        preco_ano = preco_base * (1 + (0.03 * idx))
        cotacoes.append((ano, 1, round(preco_ano, 2)))

    # Mantem fevereiro no ultimo ano para cenarios de fallback intra-ano.
    ultimo_ano = ANOS_BASE[-1]
    preco_fev = cotacoes[-1][2] * 1.008
    cotacoes.append((ultimo_ano, 2, round(preco_fev, 2)))
    return cotacoes


def montar_catalogo() -> dict[str, dict[str, dict[str, list[tuple[int, int, float]]]]]:
    return {
        "Fiat": {
            "Argo": {
                "1.0": gerar_cotacoes(78000.0),
                "Trekking 1.3": gerar_cotacoes(94000.0),
                "Drive 1.3": gerar_cotacoes(90500.0),
            },
            "Cronos": {
                "1.0": gerar_cotacoes(82000.0),
                "Drive 1.3": gerar_cotacoes(91000.0),
                "Precision 1.8": gerar_cotacoes(99500.0),
            },
            "Pulse": {
                "Drive 1.3": gerar_cotacoes(98000.0),
                "Audace Turbo 200": gerar_cotacoes(110000.0),
                "Abarth Turbo 270": gerar_cotacoes(138000.0),
            },
        },
        "Volkswagen": {
            "Polo": {
                "Track 1.0": gerar_cotacoes(93000.0),
                "TSI": gerar_cotacoes(106000.0),
                "Highline TSI": gerar_cotacoes(121000.0),
            },
            "Nivus": {
                "Comfortline": gerar_cotacoes(131000.0),
                "Highline": gerar_cotacoes(142000.0),
                "GTS": gerar_cotacoes(173000.0),
            },
            "T-Cross": {
                "Sense 200 TSI": gerar_cotacoes(119000.0),
                "Comfortline 200 TSI": gerar_cotacoes(146000.0),
                "Highline 250 TSI": gerar_cotacoes(166000.0),
            },
        },
        "Chevrolet": {
            "Onix": {
                "LT 1.0": gerar_cotacoes(87200.0),
                "LT Turbo": gerar_cotacoes(98000.0),
                "Premier Turbo": gerar_cotacoes(114000.0),
            },
            "Tracker": {
                "AT Turbo": gerar_cotacoes(128000.0),
                "LT Turbo": gerar_cotacoes(142000.0),
                "Premier Turbo": gerar_cotacoes(170000.0),
            },
            "Cruze": {
                "LT": gerar_cotacoes(125000.0),
                "LTZ": gerar_cotacoes(138000.0),
                "Premier": gerar_cotacoes(151000.0),
            },
        },
    }


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Banco nao encontrado em: {DB_PATH}. Rode antes: python src/data/init_db.py"
        )

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        dados = montar_catalogo()

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
