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


def buscar_cotacao(versao_id: int, mes: int, ano: int) -> float | None:
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT preco_medio
                FROM cotacao
                WHERE versao_id = ?
                AND mes = ?
                AND ano = ?;
                """,
                (versao_id, mes, ano),
            )
            row = cur.fetchone()
            if row:
                return row["preco_medio"]
        except sqlite3.OperationalError:
            cur.execute(
                """
                SELECT preco
                FROM cotacao
                WHERE versao_id = ?
                AND mes = ?
                AND ano = ?;
                """,
                (versao_id, mes, ano),
            )
            row = cur.fetchone()
            if row:
                return row["preco"]
        return None
    finally:
        conn.close()
