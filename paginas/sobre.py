import streamlit as st

from src.dados import CORES_STATUS, FAIXAS_STATUS

st.title("ℹ️ Sobre o Curitiba Verde")
st.write(
    "O **Curitiba Verde** é uma aplicação desenvolvida como Atividade Extensionista. "
    "O objetivo é facilitar o acesso à informação sobre a cobertura vegetal dos bairros "
    "de Curitiba e incentivar a comunidade a sugerir novos locais de plantio."
)

st.subheader("Como usar")
st.markdown(
    "1. Na página **Mapa**, clique em um bairro ou escolha um no menu lateral.\n"
    "2. Veja a cobertura vegetal e o status da região nos cards abaixo do mapa.\n"
    "3. Na página **Sugerir plantio**, envie o endereço de um local que precisa de árvores."
)

st.subheader("O que significam as cores")
for status, cor in CORES_STATUS.items():
    st.markdown(
        f"<span class='selo-status' style='--cor-status:{cor}'></span>**{status}**: cobertura vegetal {FAIXAS_STATUS[status]}",
        unsafe_allow_html=True,
    )

st.subheader("Fontes dos dados")
st.markdown(
    "- **Contornos dos bairros:** IPPUC, a partir do repositório "
    "[geo-curitiba](https://github.com/gustavokira/geo-curitiba)."
)
