import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dados import CORES_STATUS, FAIXAS_STATUS, carregar_bairros, carregar_contornos

df = carregar_bairros()
contornos = carregar_contornos()


# --- 1. SELEÇÃO DO BAIRRO (MENU LATERAL OU CLIQUE NO MAPA) ---
def bairro_clicado_no_mapa():
    pontos = st.session_state.get("mapa", {}).get("selection", {}).get("points", [])
    return pontos[0]["customdata"][0] if pontos else None


def ao_trocar_no_menu():
    # Escolha feita no menu vale mais que um clique antigo no mapa
    st.session_state["ultimo_clique"] = bairro_clicado_no_mapa()


clique = bairro_clicado_no_mapa()
if clique and clique != st.session_state.get("ultimo_clique"):
    st.session_state["bairro"] = clique
    st.session_state["ultimo_clique"] = clique

st.sidebar.markdown("---")
bairro = st.sidebar.selectbox(
    "Selecione um Bairro no Menu:", df["NOME"].unique(),
    key="bairro", on_change=ao_trocar_no_menu
)
dados = df[df["NOME"] == bairro].iloc[0]
cor_status = CORES_STATUS[dados["Status"]]

st.sidebar.markdown(f"### 📍 {bairro}")
st.sidebar.write(f"**Cobertura Vegetal:** {dados['saude_verde']}%")
st.sidebar.markdown(
    f"**Status da Região:** <span class='selo-status' style='--cor-status:{cor_status}'></span>{dados['Status']}",
    unsafe_allow_html=True,
)


# --- 2. MAPA COM O CONTORNO DOS BAIRROS ---
st.title("Mapa Interativo das Áreas Verdes de Curitiba")
st.write("Cada bairro é pintado conforme sua cobertura vegetal. Clique em um bairro para ver os dados dele.")

# Mapa claro ou escuro conforme o tema escolhido pelo usuário
tema_escuro = st.context.theme.type == "dark"
cor_divisa = "#101a12" if tema_escuro else "#ffffff"
cor_destaque = "#ffffff" if tema_escuro else "#101a12"

fig = px.choropleth_map(
    df, geojson=contornos, locations="NOME", featureidkey="properties.nome",
    color="Status", color_discrete_map=CORES_STATUS,
    category_orders={"Status": list(CORES_STATUS)},
    hover_name="NOME", custom_data=["NOME"],
    hover_data={"NOME": False, "saude_verde": True, "Status": True},
    labels={"saude_verde": "Cobertura Vegetal (%)"},
    center={"lat": -25.48, "lon": -49.28}, zoom=10, opacity=0.75, height=550
)
fig.update_traces(marker_line_color=cor_divisa, marker_line_width=1)
# Legenda com a faixa de cada status, ex.: "Crítico (abaixo de 15%)"
fig.for_each_trace(lambda t: t.update(name=f"{t.name} ({FAIXAS_STATUS[t.name]})"))

# Contorno reforçado no bairro selecionado
fig.add_trace(go.Choroplethmap(
    geojson=contornos, featureidkey="properties.nome", locations=[bairro], z=[1],
    colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
    marker_line_color=cor_destaque, marker_line_width=3,
    hoverinfo="skip", showlegend=False
))

fig.update_layout(
    map_style="carto-darkmatter" if tema_escuro else "carto-positron",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    legend={
        "title": {"text": "Status"}, "x": 0.01, "y": 0.99,
        "bgcolor": "rgba(16,26,18,0.8)" if tema_escuro else "rgba(255,255,255,0.85)",
    },
    uirevision="mapa"  # mantém o zoom do usuário depois de cada clique
)
st.plotly_chart(fig, width="stretch", key="mapa", on_select="rerun", selection_mode="points")
st.caption("As cores foram escolhidas para serem distinguíveis também por pessoas com daltonismo.")


# --- 3. CARDS INFERIORES ---
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"<div class='metric-card' style='--cor-status:{cor_status}'>"
        f"<h4>Cobertura Vegetal ({bairro})</h4><h2>{dados['saude_verde']}%</h2></div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<div class='metric-card' style='--cor-status:{CORES_STATUS['Crítico']}'>"
        f"<h4>Déficit de Árvores ({bairro})</h4><h2>{100 - dados['saude_verde']}%</h2></div>",
        unsafe_allow_html=True,
    )
