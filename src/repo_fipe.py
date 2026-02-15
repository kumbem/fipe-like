import sqlite3

from db import get_connection


def listar_marcas():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nome FROM marca ORDER BY nome;")
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def listar_modelos(marca_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nome
            FROM modelo
            WHERE marca_id = ?
            ORDER BY nome;
        """,
            (marca_id,),
        )
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def listar_versoes(modelo_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, nome
            FROM versao
            WHERE modelo_id = ?
            ORDER BY nome;
        """,
            (modelo_id,),
        )
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()


def listar_anos_disponiveis(versao_id: int | None = None) -> list[int]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        if versao_id is None:
            cur.execute(
                """
                SELECT DISTINCT ano
                FROM cotacao
                ORDER BY ano DESC;
                """
            )
        else:
            cur.execute(
                """
                SELECT DISTINCT ano
                FROM cotacao
                WHERE versao_id = ?
                ORDER BY ano DESC;
                """,
                (versao_id,),
            )
        rows = cur.fetchall()
        return [int(row["ano"]) for row in rows]
    finally:
        conn.close()


def buscar_menor_preco_ano(versao_id: int, ano: int) -> float | None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT MIN(preco_medio) AS menor_preco
                FROM cotacao
                WHERE versao_id = ?
                  AND ano = ?;
                """,
                (versao_id, ano),
            )
        except sqlite3.OperationalError:
            # Compatibilidade com schema atual (coluna preco) e legado (preco_medio).
            cur.execute(
                """
                SELECT MIN(preco) AS menor_preco
                FROM cotacao
                WHERE versao_id = ?
                  AND ano = ?;
                """,
                (versao_id, ano),
            )

        row = cur.fetchone()
        if row is None or row["menor_preco"] is None:
            return None
        return float(row["menor_preco"])
    finally:
        conn.close()


def buscar_cotacao_info(versao_id: int, mes: int, ano: int) -> dict | None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        row = None

        def consultar_com_coluna(coluna_preco: str) -> sqlite3.Row | None:
            cur.execute(
                f"""
                SELECT ano, mes, {coluna_preco} AS preco
                FROM cotacao
                WHERE versao_id = ?
                  AND (ano < ? OR (ano = ? AND mes <= ?))
                ORDER BY ano DESC, mes DESC
                LIMIT 1;
                """,
                (versao_id, ano, ano, mes),
            )
            retorno = cur.fetchone()
            if retorno is not None:
                return retorno

            # Se nao houver periodo <= solicitado, usa o primeiro periodo disponivel.
            cur.execute(
                f"""
                SELECT ano, mes, {coluna_preco} AS preco
                FROM cotacao
                WHERE versao_id = ?
                ORDER BY ano ASC, mes ASC
                LIMIT 1;
                """,
                (versao_id,),
            )
            return cur.fetchone()

        try:
            row = consultar_com_coluna("preco_medio")
        except sqlite3.OperationalError:
            # Compatibilidade com schema atual (coluna preco) e legado (preco_medio).
            row = consultar_com_coluna("preco")

        if row is None:
            return None

        return {
            "preco": float(row["preco"]),
            "mes": int(row["mes"]),
            "ano": int(row["ano"]),
            "fallback_aplicado": (int(row["mes"]) != mes or int(row["ano"]) != ano),
        }
    finally:
        conn.close()


def buscar_cotacao(versao_id: int, mes: int, ano: int) -> float | None:
    resultado = buscar_cotacao_info(versao_id, mes, ano)
    if resultado is None:
        return None
    return resultado["preco"]


def registrar_consulta(
    marca_id: int, modelo_id: int, versao_id: int, mes: int, ano: int
) -> None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO consulta_log (marca_id, modelo_id, versao_id, mes, ano)
            VALUES (?, ?, ?, ?, ?);
            """,
            (marca_id, modelo_id, versao_id, mes, ano),
        )
        conn.commit()
    finally:
        conn.close()
