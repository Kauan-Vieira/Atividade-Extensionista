import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CARREGAMENTO DOS DADOS ---
@st.cache_data
def load_data():
    df = pd.read_csv("src/Dados-Bairros/bairros_curitiba.csv")
    
    def definir_status(valor):
        if valor < 15: return "Crítico"
        elif valor < 40: return "Alerta"
        else: return "Bom"
    
    df['Status'] = df['saude_verde'].apply(definir_status)
    df['Cor_Mapa'] = df['saude_verde'].apply(lambda x: "#ea0606" if x < 40 else "#00b828")
    return df

df = load_data()

# --- 2. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Curitiba Verde", layout="wide")

# --- 3. LENDO O ARQUIVO CSS EXTERNO ---
try:
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo style.css não encontrado! Crie o arquivo na mesma pasta do app.py.")

# --- 4. SIDEBAR (MENU LATERAL) ---
st.sidebar.title("🍃 Curitiba Verde")
st.sidebar.markdown("---")
bairro = st.sidebar.selectbox("Selecione um Bairro no Menu:", df['NOME'].unique())
dados = df[df['NOME'] == bairro].iloc[0]

st.sidebar.markdown(f"### 📍 {bairro}")
st.sidebar.write(f"**Cobertura Vegetal:** {dados['saude_verde']}%")
st.sidebar.write(f"**Status da Região:** {dados['Status']}")

# --- 5. PAINEL PRINCIPAL (MAPA) ---
st.title("Mapa Interativo das Áreas Verdes de Curitiba")
st.write("Explore as regiões da cidade. Bolinhas maiores representam mais área verde.")

fig = px.scatter_mapbox(
    df, lat="Latitude", lon="Longitude", size="saude_verde", color="Cor_Mapa",
    color_discrete_map="identity", hover_name="NOME",
    hover_data={"Latitude": False, "Longitude": False, "saude_verde": True, "Status": True},
    zoom=10.5, height=550
)

# Mapa fixo no estilo claro (carto-positron)
fig.update_layout(
    mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig, use_container_width=True)

# CARDS INFERIORES
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-card'><h4>Cobertura Vegetal ({bairro})</h4><h2 style='color:#00b894 !important'>{dados['saude_verde']}%</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><h4>Déficit de Árvores ({bairro})</h4><h2 style='color:#e84118 !important'>{100 - dados['saude_verde']}%</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 6. FORMULÁRIO COM UPLOAD ---
st.subheader("🌱 Ajude a Comunidade: Sugira um Plantio")
st.write("Identificou um local com pouca vegetação na sua rua? Envie o endereço e uma foto do local.")

with st.form("form_sugestao", clear_on_submit=True):
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        endereco_input = st.text_input("Endereço completo (Rua, Número, Bairro):")
        motivo_input = st.text_area("Por que este local precisa de mais árvores?")
    with col_form2:
        foto_upload = st.file_uploader("Faça upload de uma foto do local:", type=["jpg", "jpeg", "png"])
        
    if st.form_submit_button("Enviar Sugestão de Plantio"):
        if endereco_input == "":
            st.error("⚠️ Por favor, preencha pelo menos o endereço antes de enviar.")
        else:
            st.success(f"✅ Obrigado! Sua sugestão para '{endereco_input}' foi registrada.")