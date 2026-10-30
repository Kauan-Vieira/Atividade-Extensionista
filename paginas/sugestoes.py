import streamlit as st

st.title("🌱 Ajude a Comunidade: Sugira um Plantio")
st.write("Identificou um local com pouca vegetação na sua rua? Envie o endereço e uma foto do local.")

with st.form("form_sugestao", clear_on_submit=True):
    col_form1, col_form2 = st.columns(2)
    with col_form1:
        endereco_input = st.text_input("Endereço completo (Rua, Número, Bairro):")
        motivo_input = st.text_area("Por que este local precisa de mais árvores?")
    with col_form2:
        foto_upload = st.file_uploader("Faça upload de uma foto do local:", type=["jpg", "jpeg", "png"])

    if st.form_submit_button("Enviar Sugestão de Plantio"):
        if endereco_input.strip() == "":
            st.error("⚠️ Por favor, preencha pelo menos o endereço antes de enviar.")
        else:
            st.success(f"✅ Obrigado! Sua sugestão para '{endereco_input}' foi registrada.")
