from db import get_connection
from repo_fipe import (
    buscar_cotacao,
    buscar_cotacao_info,
    listar_marcas,
    listar_modelos,
    listar_versoes,
    registrar_consulta,
)

MARCA_ALVO = "Fiat"
MES_VALIDO = 1
ANO_VALIDO = 2025
MES_FALLBACK = 3
ANO_FALLBACK = 2025
MES_FALLBACK_MULTIPLO = 11
ANO_FALLBACK_MULTIPLO = 2025
MES_SEM_HISTORICO_ANTERIOR = 12
ANO_SEM_HISTORICO_ANTERIOR = 2010
VERSAO_SEM_COTACAO = 999999


def contar_logs() -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS total FROM consulta_log;")
        return cur.fetchone()["total"]
    finally:
        conn.close()


def obter_primeiro_periodo(versao_id: int) -> tuple[int, int]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ano, mes
            FROM cotacao
            WHERE versao_id = ?
            ORDER BY ano ASC, mes ASC
            LIMIT 1;
            """,
            (versao_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("Versao de teste sem cotacao no banco.")
        return int(row["ano"]), int(row["mes"])
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
    primeiro_ano, primeiro_mes = obter_primeiro_periodo(versao["id"])

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

    # 2) Consulta com fallback deve retornar ultimo periodo anterior disponivel
    cotacao_fallback = buscar_cotacao_info(versao["id"], MES_FALLBACK, ANO_FALLBACK)
    if cotacao_fallback is None:
        raise RuntimeError("Esperava fallback de cotacao, mas veio None.")
    if not cotacao_fallback["fallback_aplicado"]:
        raise RuntimeError("Esperava fallback aplicado, mas veio periodo exato.")
    if cotacao_fallback["mes"] != 2 or cotacao_fallback["ano"] != 2025:
        raise RuntimeError(
            f"Fallback inesperado: {cotacao_fallback['mes']:02d}/{cotacao_fallback['ano']}"
        )

    print("CENARIO COM FALLBACK:")
    print(
        f"Consulta {MES_FALLBACK:02d}/{ANO_FALLBACK} -> "
        f"usou {cotacao_fallback['mes']:02d}/{cotacao_fallback['ano']}"
    )
    print(f"Preco encontrado: R$ {cotacao_fallback['preco']:.2f}")

    # 3) Consulta com fallback multiplo (11/2025 -> 02/2025 com seed atual)
    cotacao_fallback_multiplo = buscar_cotacao_info(
        versao["id"], MES_FALLBACK_MULTIPLO, ANO_FALLBACK_MULTIPLO
    )
    if cotacao_fallback_multiplo is None:
        raise RuntimeError("Esperava fallback multiplo, mas veio None.")
    if not cotacao_fallback_multiplo["fallback_aplicado"]:
        raise RuntimeError("Esperava fallback multiplo aplicado, mas veio periodo exato.")
    if cotacao_fallback_multiplo["mes"] != 2 or cotacao_fallback_multiplo["ano"] != 2025:
        raise RuntimeError(
            "Fallback multiplo inesperado: "
            f"{cotacao_fallback_multiplo['mes']:02d}/{cotacao_fallback_multiplo['ano']}"
        )

    print("CENARIO COM FALLBACK MULTIPLO:")
    print(
        f"Consulta {MES_FALLBACK_MULTIPLO:02d}/{ANO_FALLBACK_MULTIPLO} -> "
        f"usou {cotacao_fallback_multiplo['mes']:02d}/{cotacao_fallback_multiplo['ano']}"
    )
    print(f"Preco encontrado: R$ {cotacao_fallback_multiplo['preco']:.2f}")

    # 4) Sem historico anterior: deve usar primeiro periodo disponivel
    cotacao_sem_historico_anterior = buscar_cotacao_info(
        versao["id"], MES_SEM_HISTORICO_ANTERIOR, ANO_SEM_HISTORICO_ANTERIOR
    )
    if cotacao_sem_historico_anterior is None:
        raise RuntimeError("Esperava fallback para primeiro periodo disponivel, mas veio None.")
    if (
        cotacao_sem_historico_anterior["mes"] != primeiro_mes
        or cotacao_sem_historico_anterior["ano"] != primeiro_ano
    ):
        raise RuntimeError(
            "Fallback para primeiro periodo disponivel inesperado: "
            f"{cotacao_sem_historico_anterior['mes']:02d}/{cotacao_sem_historico_anterior['ano']}"
        )

    print("CENARIO SEM HISTORICO ANTERIOR:")
    print(
        f"Consulta {MES_SEM_HISTORICO_ANTERIOR:02d}/{ANO_SEM_HISTORICO_ANTERIOR} -> "
        f"usou {cotacao_sem_historico_anterior['mes']:02d}/"
        f"{cotacao_sem_historico_anterior['ano']}"
    )
    print(f"Preco encontrado: R$ {cotacao_sem_historico_anterior['preco']:.2f}")

    # 5) Consulta realmente sem cotacao (versao inexistente) nao deve registrar
    antes_sem = contar_logs()
    preco_sem = buscar_cotacao(VERSAO_SEM_COTACAO, 1, 2024)
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
