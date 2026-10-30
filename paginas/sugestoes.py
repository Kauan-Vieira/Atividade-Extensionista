import logging

import streamlit as st

from src import planilha
from src.dados import carregar_bairros

bairros = list(carregar_bairros()["NOME"].sort_values())


def enviar_sugestao():
    bairro = st.session_state["form_bairro"]
    endereco = st.session_state["form_endereco"].strip()
    motivo = st.session_state["form_motivo"].strip()

    if not bairro or not endereco:
        st.session_state["resultado_envio"] = ("erro", "⚠️ Por favor, escolha o bairro e preencha o endereço antes de enviar.")
        return
    if not planilha.planilha_configurada():
        st.session_state["resultado_envio"] = ("erro", "⚠️ O envio de sugestões ainda não está configurado. Tente novamente mais tarde.")
        return
    try:
        planilha.salvar_sugestao(bairro, endereco, motivo)
    except Exception:
        logging.exception("Erro ao salvar sugestão na planilha")
        st.session_state["resultado_envio"] = ("erro", "⚠️ Não foi possível enviar sua sugestão agora. Tente novamente em alguns minutos.")
        return

    st.session_state["resultado_envio"] = ("sucesso", f"✅ Obrigado! Sua sugestão para '{endereco}' ({bairro}) foi registrada.")
    # Só limpa o formulário quando a sugestão foi salva
    st.session_state["form_endereco"] = ""
    st.session_state["form_motivo"] = ""


# Já vem marcado o bairro escolhido na página do mapa, se houver
if "form_bairro" not in st.session_state and st.session_state.get("bairro") in bairros:
    st.session_state["form_bairro"] = st.session_state["bairro"]

st.title("🌱 Ajude a Comunidade: Sugira um Plantio")
st.write("Identificou um local com pouca vegetação na sua rua? Envie o endereço e conte por que ele precisa de árvores.")

with st.form("form_sugestao"):
    st.selectbox("Bairro:", bairros, index=None, placeholder="Escolha o bairro", key="form_bairro")
    st.text_input("Endereço (Rua e Número):", max_chars=200, key="form_endereco")
    st.text_area("Por que este local precisa de mais árvores?", max_chars=1000, key="form_motivo")
    st.form_submit_button("Enviar Sugestão de Plantio", on_click=enviar_sugestao)

if "resultado_envio" in st.session_state:
    tipo, mensagem = st.session_state.pop("resultado_envio")
    if tipo == "sucesso":
        st.success(mensagem)
    else:
        st.error(mensagem)
