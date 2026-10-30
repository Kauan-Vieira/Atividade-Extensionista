"""Leitura e preparação dos dados dos bairros de Curitiba."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

PASTA_DADOS = Path(__file__).resolve().parent / "Dados-Bairros"

# Paleta testada em simulações de deuteranopia, protanopia e tritanopia:
# as três cores continuam distinguíveis entre si para pessoas com daltonismo.
CORES_STATUS = {
    "Crítico": "#B2182B",  # vermelho
    "Alerta": "#F2B134",   # amarelo
    "Bom": "#1F8A9E",      # azul-petróleo
}
FAIXAS_STATUS = {
    "Crítico": "abaixo de 15%",
    "Alerta": "de 15% a 39%",
    "Bom": "40% ou mais",
}


def definir_status(cobertura):
    if cobertura < 15:
        return "Crítico"
    elif cobertura < 40:
        return "Alerta"
    return "Bom"


@st.cache_data
def carregar_bairros():
    df = pd.read_csv(PASTA_DADOS / "bairros_curitiba.csv")
    df["Status"] = df["saude_verde"].apply(definir_status)
    return df


@st.cache_data
def carregar_contornos():
    """Contornos dos bairros (IPPUC), com o nome do bairro em properties.nome."""
    with open(PASTA_DADOS / "bairros_curitiba.geojson", encoding="utf-8") as f:
        return json.load(f)
