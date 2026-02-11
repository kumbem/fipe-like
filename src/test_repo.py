from repo_fipe import buscar_cotacao, listar_marcas, listar_modelos, listar_versoes

MARCA_ALVO = "Fiat"
MES_ALVO = 1
ANO_ALVO = 2024


def main() -> None:
    marcas = listar_marcas()
    marca = next((m for m in marcas if m["nome"] == MARCA_ALVO), None)

    if not marca:
        disponiveis = ", ".join(m["nome"] for m in marcas) if marcas else "nenhuma"
        print(
            f"Marca '{MARCA_ALVO}' nao encontrada. "
            f"Marcas disponiveis: {disponiveis}."
        )
        return

    modelos = listar_modelos(marca["id"])

    if not modelos:
        print(f"Nenhum modelo encontrado para a marca {marca['nome']}.")
        return

    modelo = modelos[0]
    versoes = listar_versoes(modelo["id"])

    if not versoes:
        print(
            f"Nenhuma versao encontrada para {marca['nome']} - {modelo['nome']}."
        )
        return

    versao = versoes[0]
    preco = buscar_cotacao(versao["id"], MES_ALVO, ANO_ALVO)

    print("COTACAO:")
    if preco is None:
        print("Sem cotacao encontrada")
        return

    print(f"R$ {preco:.2f}")


if __name__ == "__main__":
    main()
