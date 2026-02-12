from db import get_connection
from repo_fipe import (
    buscar_cotacao,
    listar_marcas,
    listar_modelos,
    listar_versoes,
    registrar_consulta,
)

MARCA_ALVO = "Fiat"
MES_VALIDO = 1
ANO_VALIDO = 2025
MES_SEM_COTACAO = 1
ANO_SEM_COTACAO = 2024


def contar_logs() -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM consulta_log;")
        return cur.fetchone()["total"]
    finally:
        conn.close()


def selecionar_fluxo_base():
    marcas = listar_marcas()
    marca = next((m for m in marcas if m["nome"] == MARCA_ALVO), None)
    if not marca:
        raise RuntimeError(f"Marca alvo nao encontrada: {MARCA_ALVO}")

    modelos = listar_modelos(marca["id"])
    if not modelos:
        raise RuntimeError(f"Nenhum modelo encontrado para: {marca['nome']}")

    modelo = modelos[0]
    versoes = listar_versoes(modelo["id"])
    if not versoes:
        raise RuntimeError(
            f"Nenhuma versao encontrada para: {marca['nome']} - {modelo['nome']}"
        )

    versao = versoes[0]
    return marca, modelo, versao


def main() -> None:
    marca, modelo, versao = selecionar_fluxo_base()

    print(f"Fluxo base: {marca['nome']} / {modelo['nome']} / {versao['nome']}")

    # 1) Consulta valida deve registrar 1 novo log
    antes_valido = contar_logs()
    preco_valido = buscar_cotacao(versao["id"], MES_VALIDO, ANO_VALIDO)

    if preco_valido is None:
        raise RuntimeError("Esperava cotacao valida, mas veio None.")

    registrar_consulta(
        marca["id"],
        modelo["id"],
        versao["id"],
        MES_VALIDO,
        ANO_VALIDO,
    )
    depois_valido = contar_logs()

    print("CENARIO VALIDO:")
    print(f"Preco encontrado: R$ {preco_valido:.2f}")
    print(f"Logs antes/depois: {antes_valido} -> {depois_valido}")
    print(f"Incremento esperado (1): {depois_valido - antes_valido}")

    # 2) Consulta sem cotacao nao deve registrar
    antes_sem = contar_logs()
    preco_sem = buscar_cotacao(versao["id"], MES_SEM_COTACAO, ANO_SEM_COTACAO)
    if preco_sem is None:
        pass
    else:
        raise RuntimeError(
            "Esperava sem cotacao no cenario negativo, mas houve valor retornado."
        )
    depois_sem = contar_logs()

    print("CENARIO SEM COTACAO:")
    print("Sem cotacao encontrada")
    print(f"Logs antes/depois: {antes_sem} -> {depois_sem}")
    print(f"Incremento esperado (0): {depois_sem - antes_sem}")


if __name__ == "__main__":
    main()
