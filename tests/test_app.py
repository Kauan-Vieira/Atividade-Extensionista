from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.dados import CORES_STATUS, carregar_bairros, carregar_contornos, definir_status

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app():
    return AppTest.from_file(APP, default_timeout=60).run()


# --- DADOS ---
def test_csv_tem_os_75_bairros_sem_repeticao():
    df = carregar_bairros()
    assert len(df) == 75
    assert df["NOME"].is_unique
    assert not df.isna().any().any()


def test_todo_bairro_do_csv_tem_contorno():
    nomes_contornos = {f["properties"]["nome"] for f in carregar_contornos()["features"]}
    assert set(carregar_bairros()["NOME"]) == nomes_contornos


@pytest.mark.parametrize("cobertura, status", [
    (0, "Crítico"), (14, "Crítico"), (15, "Alerta"), (39, "Alerta"), (40, "Bom"), (100, "Bom"),
])
def test_faixas_de_status(cobertura, status):
    assert definir_status(cobertura) == status
    assert status in CORES_STATUS


# --- PÁGINA DO MAPA ---
def test_mapa_abre_sem_erros(app):
    assert not app.exception
    assert len(app.selectbox[0].options) == 75


def test_trocar_bairro_no_menu_atualiza_a_tela(app):
    app.selectbox[0].select("BATEL").run()
    assert not app.exception
    assert any("BATEL" in m.value for m in app.sidebar.markdown)


# --- PÁGINA DE SUGESTÕES ---
def test_sugestao_sem_endereco_mostra_aviso(app):
    app.switch_page("paginas/sugestoes.py").run()
    app.button[0].click().run()
    assert app.error and "endereço" in app.error[0].value


def test_sugestao_com_endereco_mostra_sucesso(app):
    app.switch_page("paginas/sugestoes.py").run()
    app.text_input[0].input("Rua das Flores, 100")
    app.button[0].click().run()
    assert app.success and "Rua das Flores, 100" in app.success[0].value


def test_pagina_sobre_abre_sem_erros(app):
    app.switch_page("paginas/sobre.py").run()
    assert not app.exception


def test_bairro_escolhido_continua_ao_voltar_para_o_mapa(app):
    app.selectbox[0].select("BATEL").run()
    app.switch_page("paginas/sobre.py").run()
    app.switch_page("paginas/mapa.py").run()
    assert app.selectbox[0].value == "BATEL"
