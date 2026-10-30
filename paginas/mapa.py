import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.dados import (
    CORES_STATUS, FAIXAS_STATUS, META_ARBOREA, carregar_bairros, carregar_contornos,
    carregar_fontes, carregar_historico, formatar_pct,
)

df = carregar_bairros()
df["Cobertura de árvores"] = df["cobertura_arborea"].apply(formatar_pct)
contornos = carregar_contornos()
historico = carregar_historico()
fontes = carregar_fontes()
ano_arborea = fontes["cobertura_arborea"]["ano"]


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
st.sidebar.write(f"**Cobertura de árvores:** {formatar_pct(dados['cobertura_arborea'])}")
st.sidebar.markdown(
    f"**Status da Região:** <span class='selo-status' style='--cor-status:{cor_status}'></span>{dados['Status']}",
    unsafe_allow_html=True,
)


# --- 2. MAPA COM O CONTORNO DOS BAIRROS ---
st.title("Mapa Interativo das Áreas Verdes de Curitiba")
st.write(
    f"Cada bairro é pintado conforme a parte da sua área coberta por árvores. A meta é de pelo menos "
    f"{META_ARBOREA}% de copa de árvores por bairro (regra 3-30-300). Clique em um bairro para ver os dados dele."
)

# Mapa claro ou escuro conforme o tema escolhido pelo usuário
tema_escuro = st.context.theme.type == "dark"
cor_divisa = "#101a12" if tema_escuro else "#ffffff"
cor_destaque = "#ffffff" if tema_escuro else "#101a12"

fig = px.choropleth_map(
    df, geojson=contornos, locations="NOME", featureidkey="properties.nome",
    color="Status", color_discrete_map=CORES_STATUS,
    category_orders={"Status": list(CORES_STATUS)},
    hover_name="NOME", custom_data=["NOME"],
    hover_data={"NOME": False, "Cobertura de árvores": True, "Status": True},
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
st.caption(
    f"Cobertura de árvores: ESA WorldCover {ano_arborea}, imagens de satélite com 10 m de resolução. "
    "As cores foram escolhidas para serem distinguíveis também por pessoas com daltonismo."
)


# --- 3. CARDS INFERIORES ---
serie = historico[historico["NOME"] == bairro].sort_values("ano")
primeiro, ultimo = serie.iloc[0], serie.iloc[-1]
variacao = ultimo["vegetacao"] - primeiro["vegetacao"]
# Variações abaixo de meio ponto ficam dentro da margem de erro do mapa
cor_tendencia = (CORES_STATUS["Crítico"] if variacao <= -0.5
                 else CORES_STATUS["Bom"] if variacao >= 0.5 else "rgba(127,127,127,0.6)")

if max(primeiro["vegetacao"], ultimo["vegetacao"]) < 1:
    # Bairro quase todo classificado como área urbanizada: o MapBiomas não mede o verde dele
    detalhe_tendencia = "Nesta fonte, o bairro inteiro conta como área urbanizada"
else:
    detalhe_tendencia = (f"De {formatar_pct(primeiro['vegetacao'])} para "
                         f"{formatar_pct(ultimo['vegetacao'])} da área do bairro")

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f"<div class='metric-card' style='--cor-status:{cor_status}'>"
        f"<h4>Cobertura de árvores ({bairro})</h4><h2>{formatar_pct(dados['cobertura_arborea'])}</h2>"
        f"<p>Meta: {META_ARBOREA}% · dados de {ano_arborea}</p></div>",
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"<div class='metric-card' style='--cor-status:{cor_tendencia}'>"
        f"<h4>Vegetação de {primeiro['ano']} a {ultimo['ano']} ({bairro})</h4>"
        f"<h2>{formatar_pct(variacao, sinal=True)}</h2>"
        f"<p>{detalhe_tendencia}</p></div>",
        unsafe_allow_html=True,
    )


# --- 4. EVOLUÇÃO DA VEGETAÇÃO ---
st.subheader("📈 Evolução da vegetação")
media_cidade = historico.groupby("ano", as_index=False)["vegetacao"].mean()
evolucao = pd.concat([
    serie.assign(Série=bairro)[["ano", "vegetacao", "Série"]],
    media_cidade.assign(Série="Média dos bairros de Curitiba"),
])
fig_evolucao = px.line(
    evolucao, x="ano", y="vegetacao", color="Série", markers=True,
    labels={"ano": "Ano", "vegetacao": "Vegetação (% da área)", "Série": ""}, height=320,
)
fig_evolucao.for_each_trace(lambda t: t.update(
    line={"color": "#17707F", "width": 3} if t.name == bairro else {"color": "#8a8a8a", "dash": "dash"}
))
fig_evolucao.update_layout(margin={"t": 10}, legend={"orientation": "h", "y": -0.25}, xaxis={"dtick": 1})
st.plotly_chart(fig_evolucao, width="stretch")
st.caption(
    "Vegetação inclui árvores, campos, áreas úmidas, silvicultura e pastagens. Fonte: MapBiomas (coleção de "
    "10 m), atualizado todo ano. Os números são menores que os de árvores do mapa porque, nesta fonte, "
    "o verde dentro das áreas urbanizadas (árvores de rua e quintais) conta como área urbana."
)
