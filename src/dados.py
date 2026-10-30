"""Leitura e preparação dos dados dos bairros de Curitiba."""
import json
import unicodedata
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

# Regra 3-30-300: cada bairro deveria ter pelo menos 30% de copa de árvores
META_ARBOREA = 30
FAIXAS_STATUS = {
    "Crítico": "abaixo de 15%",
    "Alerta": "de 15% a 29%",
    "Bom": "30% ou mais",
}


def definir_status(cobertura):
    if cobertura < META_ARBOREA / 2:
        return "Crítico"
    elif cobertura < META_ARBOREA:
        return "Alerta"
    return "Bom"


def formatar_pct(valor, sinal=False):
    """Porcentagem no formato brasileiro, ex.: 13,6% ou +1,3 p.p."""
    texto = f"{valor:+.1f}" if sinal else f"{valor:.1f}"
    return texto.replace(".", ",") + (" p.p." if sinal else "%")


def sem_acento(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


@st.cache_data
def carregar_bairros():
    """Cobertura de árvores por bairro (ESA WorldCover 2021), em ordem alfabética."""
    df = pd.read_csv(PASTA_DADOS / "bairros_curitiba.csv")
    df["Status"] = df["cobertura_arborea"].apply(definir_status)
    # Ordena ignorando acentos, para ÁGUA VERDE ficar no começo e não no fim
    return df.sort_values("NOME", key=lambda nomes: nomes.map(sem_acento)).reset_index(drop=True)


@st.cache_data
def carregar_historico():
    """Vegetação por bairro e ano (MapBiomas 10 m), atualizada pelo robô de coleta."""
    return pd.read_csv(PASTA_DADOS / "historico_vegetacao.csv")


@st.cache_data
def carregar_fontes():
    with open(PASTA_DADOS / "fontes.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def carregar_contornos():
    """Contornos dos bairros (IPPUC), com o nome do bairro em properties.nome."""
    with open(PASTA_DADOS / "bairros_curitiba.geojson", encoding="utf-8") as f:
        return json.load(f)
