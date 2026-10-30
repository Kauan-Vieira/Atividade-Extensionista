import streamlit as st
from pathlib import Path

# Caminhos relativos à pasta do app.py (funciona de qualquer diretório)
BASE_DIR = Path(__file__).resolve().parent

# --- 1. CONFIGURAÇÃO DA INTERFACE (deve ser o primeiro comando do Streamlit) ---
st.set_page_config(page_title="Curitiba Verde", page_icon="🍃", layout="wide")

# --- 2. LENDO O ARQUIVO CSS EXTERNO ---
try:
    with open(BASE_DIR / "style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Arquivo style.css não encontrado! Crie o arquivo na mesma pasta do app.py.")

# Mantém o bairro escolhido ao trocar de página (o Streamlit apaga o estado
# de widgets que não aparecem na página atual)
if "bairro" in st.session_state:
    st.session_state["bairro"] = st.session_state["bairro"]

# --- 3. NAVEGAÇÃO ENTRE PÁGINAS ---
pagina = st.navigation([
    st.Page("paginas/mapa.py", title="Mapa", icon="🗺️", default=True),
    st.Page("paginas/sugestoes.py", title="Sugerir plantio", icon="🌱"),
    st.Page("paginas/sobre.py", title="Sobre o projeto", icon="ℹ️"),
], position="top")

st.sidebar.title("🍃 Curitiba Verde")
pagina.run()
