import streamlit as st

from repo_fipe import (
    buscar_cotacao_info,
    buscar_menor_preco_ano,
    listar_anos_disponiveis,
    listar_marcas,
    listar_modelos,
    listar_versoes,
    registrar_consulta,
)

st.set_page_config(
    page_title="Deep FIPE Seek",
    page_icon=":car:",
    layout="centered",
)

st.markdown(
    """
    <style>
      .stApp {
        background: #000000;
      }
      .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp p, .stApp div, .stApp span {
        color: #ffffff;
      }
      div[data-testid="stVerticalBlock"] > div:has(> div > div > div.stButton) {
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid #cfe0ff;
        border-radius: 12px;
        padding: 0.8rem;
        box-shadow: 0 8px 20px rgba(15, 47, 102, 0.08);
      }
      .mini-col {
        margin-top: 2.2rem;
      }
      .mini-card {
        background: #000000;
        border: 1px solid #2e2e2e;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45);
        text-align: center;
        margin-bottom: 0.7rem;
        padding: 0.5rem 0.4rem;
      }
      .mini-icon {
        font-size: 1.5rem;
        line-height: 1.2;
      }
      .mini-label {
        font-size: 0.76rem;
        color: #ffffff;
      }
      .centered-text {
        text-align: center;
      }
      div[data-testid="stAlert"] {
        text-align: center;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="centered-text">Deep FIPE Seek</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="centered-text">Selecione marca, modelo, versao, mes e ano para consultar o preco medio.</p>',
    unsafe_allow_html=True,
)

MESES_NOMINAIS = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


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
def carregar_cotacao(versao_id: int, mes: int, ano: int) -> dict | None:
    return buscar_cotacao_info(versao_id, mes, ano)


@st.cache_data
def carregar_anos(versao_id: int | None) -> list[int]:
    return listar_anos_disponiveis(versao_id)


@st.cache_data
def carregar_menor_preco_ano(versao_id: int, ano: int) -> float | None:
    return buscar_menor_preco_ano(versao_id, ano)


def format_brl(valor: float) -> str:
    base = f"{valor:,.2f}"
    return base.replace(",", "_").replace(".", ",").replace("_", ".")


left_col, main_container, right_col = st.columns([1, 3, 1], gap="large")
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

    mes = st.selectbox(
        "Mes",
        options=list(range(1, 13)),
        index=0,
        format_func=lambda m: MESES_NOMINAIS[m],
    )
    anos_disponiveis = carregar_anos(versao_sel["id"] if versao_sel is not None else None)
    ano = st.selectbox("Ano", options=anos_disponiveis, index=0)

    consultar = st.button("Consultar", type="primary", disabled=versao_sel is None)

with left_col:
    st.markdown(
        """
        <div class="mini-col">
          <div class="mini-card"><div class="mini-icon">&#128011;&#128663;</div><div class="mini-label">WhaleCar</div></div>
          <div class="mini-card"><div class="mini-icon">&#128011;</div><div class="mini-label">Whale</div></div>
          <div class="mini-card"><div class="mini-icon">&#128663;</div><div class="mini-label">Car</div></div>
          <div class="mini-card"><div class="mini-icon">&#128674;</div><div class="mini-label">Boat</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right_col:
    st.markdown(
        """
        <div class="mini-col">
          <div class="mini-card"><div class="mini-icon">&#128011;&#128663;</div><div class="mini-label">WhaleCar</div></div>
          <div class="mini-card"><div class="mini-icon">&#128674;</div><div class="mini-label">Boat</div></div>
          <div class="mini-card"><div class="mini-icon">&#128663;</div><div class="mini-label">Car</div></div>
          <div class="mini-card"><div class="mini-icon">&#128011;</div><div class="mini-label">Whale</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with resultado_container:
    st.markdown('<h3 class="centered-text">Resultado</h3>', unsafe_allow_html=True)

    if consultar and versao_sel is not None:
        cotacao = carregar_cotacao(versao_sel["id"], mes, ano)
        if cotacao is None:
            st.info("Sem cotacao para o periodo selecionado")
        else:
            preco = cotacao["preco"]
            mes_usado = cotacao["mes"]
            ano_usado = cotacao["ano"]
            fallback_aplicado = cotacao["fallback_aplicado"]

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

            if fallback_aplicado:
                mes_solicitado_nome = MESES_NOMINAIS[mes]
                mes_usado_nome = MESES_NOMINAIS[mes_usado]
                st.warning(
                    f"Sem cotacao em {mes_solicitado_nome}/{ano}. "
                    f"Usando ultimo periodo disponivel: {mes_usado_nome}/{ano_usado}."
                )

            menor_preco_ano = carregar_menor_preco_ano(versao_sel["id"], ano_usado)
            if menor_preco_ano is not None and abs(preco - menor_preco_ano) < 0.01:
                st.balloons()
                st.success("Menor preco do ano para esta versao!")

            st.success(f"Preco medio: R$ {format_brl(preco)}")
    else:
        st.markdown(
            '<p class="centered-text">O resultado da consulta aparecera aqui.</p>',
            unsafe_allow_html=True,
        )
