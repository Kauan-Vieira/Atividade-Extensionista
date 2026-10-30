"""Gravação das sugestões de plantio numa planilha do Google Sheets.

As credenciais ficam em .streamlit/secrets.toml (fora do Git) ou nos
Secrets do Streamlit Cloud. Veja .streamlit/secrets.toml.example.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
import streamlit as st

CABECALHO = ["Data e hora", "Bairro", "Endereço", "Motivo"]
FUSO_CURITIBA = ZoneInfo("America/Sao_Paulo")


def planilha_configurada():
    try:
        return "gcp_service_account" in st.secrets and "planilha_url" in st.secrets.get("sugestoes", {})
    except FileNotFoundError:
        return False


@st.cache_resource
def _aba_sugestoes():
    cliente = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    aba = cliente.open_by_url(st.secrets["sugestoes"]["planilha_url"]).sheet1
    if not aba.row_values(1):  # planilha nova: escreve o cabeçalho
        aba.insert_row(CABECALHO, 1)
    return aba


def salvar_sugestao(bairro, endereco, motivo):
    agora = datetime.now(FUSO_CURITIBA).strftime("%d/%m/%Y %H:%M")
    # RAW grava o texto como está: um "=" digitado não vira fórmula na planilha
    _aba_sugestoes().append_row([agora, bairro, endereco, motivo], value_input_option="RAW")
