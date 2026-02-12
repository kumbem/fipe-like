import streamlit as st

from repo_fipe import (
    buscar_cotacao,
    listar_marcas,
    listar_modelos,
    listar_versoes,
    registrar_consulta,
)

st.set_page_config(
    page_title="Consulta FIPE",
    page_icon=":car:",
    layout="centered",
)

st.title("Consulta FIPE")
st.caption("Selecione marca, modelo, versao, mes e ano para consultar o preco medio.")


@st.cache_data
def carregar_marcas() -> list[dict]:
    return [dict(m) for m in listar_marcas()]


@st.cache_data
def carregar_modelos(marca_id: int) -> list[dict]:
    return [dict(m) for m in listar_modelos(marca_id)]


@st.cache_data
def carregar_versoes(modelo_id: int) -> list[dict]:
    return [dict(v) for v in listar_versoes(modelo_id)]


@st.cache_data
def carregar_cotacao(versao_id: int, mes: int, ano: int) -> float | None:
    return buscar_cotacao(versao_id, mes, ano)


def format_brl(valor: float) -> str:
    base = f"{valor:,.2f}"
    return base.replace(",", "_").replace(".", ",").replace("_", ".")


main_container = st.container()
resultado_container = st.container()

with main_container:
    st.subheader("Selecao")

    marcas = carregar_marcas()
    marca_sel = st.selectbox(
        "Marca",
        options=marcas,
        format_func=lambda m: m["nome"],
        index=None,
        placeholder="Selecione uma marca",
    )

    modelo_sel = None
    versao_sel = None

    if marca_sel is not None:
        modelos = carregar_modelos(marca_sel["id"])
        if modelos:
            modelo_sel = st.selectbox(
                "Modelo",
                options=modelos,
                format_func=lambda m: m["nome"],
                index=None,
                placeholder="Selecione um modelo",
            )
        else:
            st.warning("Nenhum modelo encontrado para a marca selecionada.")

    if modelo_sel is not None:
        versoes = carregar_versoes(modelo_sel["id"])
        if versoes:
            versao_sel = st.selectbox(
                "Versao",
                options=versoes,
                format_func=lambda v: v["nome"],
                index=None,
                placeholder="Selecione uma versao",
            )
        else:
            st.warning("Nenhuma versao encontrada para o modelo selecionado.")

    mes = st.selectbox("Mes", options=list(range(1, 13)), index=0)
    ano = st.selectbox("Ano", options=[2023, 2024, 2025], index=2)

    consultar = st.button("Consultar", type="primary", disabled=versao_sel is None)

with resultado_container:
    st.subheader("Resultado")

    if consultar and versao_sel is not None:
        preco = carregar_cotacao(versao_sel["id"], mes, ano)
        if preco is None:
            st.info("Sem cotacao para o periodo selecionado")
        else:
            try:
                registrar_consulta(
                    marca_sel["id"],
                    modelo_sel["id"],
                    versao_sel["id"],
                    mes,
                    ano,
                )
            except Exception:
                # logging nao pode interromper o fluxo principal
                pass
            st.success(f"Preco medio: R$ {format_brl(preco)}")
    else:
        st.caption("O resultado da consulta aparecera aqui.")
