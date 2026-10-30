import streamlit as st

from src.dados import CORES_STATUS, FAIXAS_STATUS, META_ARBOREA, carregar_fontes

fontes = carregar_fontes()
anos = fontes["historico_vegetacao"]["anos"]

st.title("ℹ️ Sobre o Curitiba Verde")
st.write(
    "O **Curitiba Verde** é uma aplicação desenvolvida como Atividade Extensionista. "
    "O objetivo é facilitar o acesso à informação sobre a cobertura vegetal dos bairros "
    "de Curitiba e incentivar a comunidade a sugerir novos locais de plantio."
)

st.subheader("Como usar")
st.markdown(
    "1. Na página **Mapa**, clique em um bairro ou escolha um no menu lateral.\n"
    "2. Veja a cobertura de árvores, o status e a evolução da vegetação do bairro abaixo do mapa.\n"
    "3. Na página **Sugerir plantio**, envie o endereço de um local que precisa de árvores."
)

st.subheader("O que significam as cores")
st.write(
    f"O status segue a **regra 3-30-300**, uma diretriz internacional de floresta urbana que recomenda "
    f"pelo menos {META_ARBOREA}% de copa de árvores em cada bairro."
)
for status, cor in CORES_STATUS.items():
    st.markdown(
        f"<span class='selo-status' style='--cor-status:{cor}'></span>**{status}**: cobertura de árvores {FAIXAS_STATUS[status]}",
        unsafe_allow_html=True,
    )

st.subheader("Fontes dos dados")
st.markdown(
    f"- **Cobertura de árvores (mapa e status):** [ESA WorldCover](https://esa-worldcover.org/), "
    f"ano {fontes['cobertura_arborea']['ano']}. Mapa de uso do solo feito com imagens dos satélites "
    "Sentinel-1 e Sentinel-2, com 10 m de resolução. Contamos a parte da área de cada bairro "
    "classificada como árvores.\n"
    f"- **Evolução da vegetação ({anos[0]} a {anos[-1]}):** [MapBiomas](https://brasil.mapbiomas.org/), "
    "coleção de 10 m. Inclui árvores, campos, áreas úmidas, silvicultura e pastagens. "
    "Um robô confere todo mês se saiu um ano novo e propõe a atualização.\n"
    "- **Contornos dos bairros:** IPPUC, a partir do repositório "
    "[geo-curitiba](https://github.com/gustavokira/geo-curitiba).\n"
    "- **Regra 3-30-300:** Konijnendijk, C. C. (2023). *Evidence-based guidelines for greener, "
    "healthier, more resilient neighbourhoods: Introducing the 3–30–300 rule.* Journal of "
    "Forestry Research, 34, 821–830."
)

st.subheader("Limitações")
st.markdown(
    "- Com 10 m de resolução, árvores isoladas pequenas podem não aparecer, e um pixel com parte "
    "de árvore e parte de calçada é classificado pelo que predomina.\n"
    "- As duas fontes medem coisas diferentes: o WorldCover enxerga as árvores dentro da cidade, e o "
    "MapBiomas conta o verde das áreas urbanizadas como área urbana. Por isso os números da "
    "evolução são menores que os do mapa. Use a evolução para ver a **tendência** do bairro."
)
