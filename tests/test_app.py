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
@pytest.fixture
def planilha_falsa(monkeypatch):
    """Substitui a gravação no Google Sheets por uma lista em memória."""
    from src import planilha

    salvas = []
    monkeypatch.setattr(planilha, "planilha_configurada", lambda: True)
    monkeypatch.setattr(planilha, "salvar_sugestao", lambda *linha: salvas.append(linha))
    return salvas


def abrir_sugestoes(app):
    app.switch_page("paginas/sugestoes.py").run()
    return app


def preencher(app, bairro="BATEL", endereco="Rua das Flores, 100", motivo="Rua sem sombra"):
    app.selectbox(key="form_bairro").set_value(bairro)
    app.text_input(key="form_endereco").input(endereco)
    app.text_area(key="form_motivo").input(motivo)
    app.button[0].click().run()


def test_sugestao_sem_endereco_mostra_aviso(app, planilha_falsa):
    preencher(abrir_sugestoes(app), endereco="")
    assert app.error and "endereço" in app.error[0].value
    assert planilha_falsa == []


def test_sugestao_sem_bairro_mostra_aviso_e_mantem_o_texto(app, planilha_falsa):
    preencher(abrir_sugestoes(app), bairro=None)
    assert app.error and "bairro" in app.error[0].value
    assert app.text_input(key="form_endereco").value == "Rua das Flores, 100"
    assert planilha_falsa == []


def test_sugestao_completa_e_salva_e_limpa_o_formulario(app, planilha_falsa):
    preencher(abrir_sugestoes(app), endereco="  Rua das Flores, 100  ")
    assert not app.exception
    assert app.success and "Rua das Flores, 100" in app.success[0].value
    assert planilha_falsa == [("BATEL", "Rua das Flores, 100", "Rua sem sombra")]
    assert app.text_input(key="form_endereco").value == ""


def test_erro_ao_salvar_mostra_aviso_e_mantem_o_texto(app, monkeypatch):
    from src import planilha

    def falhar(*_):
        raise ConnectionError("sem internet")

    monkeypatch.setattr(planilha, "planilha_configurada", lambda: True)
    monkeypatch.setattr(planilha, "salvar_sugestao", falhar)
    preencher(abrir_sugestoes(app))
    assert app.error and "Não foi possível" in app.error[0].value
    assert app.text_input(key="form_endereco").value == "Rua das Flores, 100"


def test_sem_planilha_configurada_nao_finge_que_salvou(app):
    preencher(abrir_sugestoes(app))
    assert not app.success
    assert app.error and "não está configurado" in app.error[0].value


def test_formulario_ja_vem_com_o_bairro_do_mapa(app):
    app.selectbox[0].select("XAXIM").run()
    abrir_sugestoes(app)
    assert app.selectbox(key="form_bairro").value == "XAXIM"


def test_pagina_sobre_abre_sem_erros(app):
    app.switch_page("paginas/sobre.py").run()
    assert not app.exception


def test_bairro_escolhido_continua_ao_voltar_para_o_mapa(app):
    app.selectbox[0].select("BATEL").run()
    app.switch_page("paginas/sobre.py").run()
    app.switch_page("paginas/mapa.py").run()
    assert app.selectbox[0].value == "BATEL"


def test_salvar_sugestao_grava_a_linha_como_texto(monkeypatch):
    from src import planilha

    class AbaFalsa:
        linhas = []

        def append_row(self, valores, value_input_option):
            self.linhas.append((valores, value_input_option))

    aba = AbaFalsa()
    monkeypatch.setattr(planilha, "_aba_sugestoes", lambda: aba)
    planilha.salvar_sugestao("BATEL", "=Rua X, 10", "motivo")

    (data, *resto), modo = aba.linhas[0]
    assert resto == ["BATEL", "=Rua X, 10", "motivo"]
    assert modo == "RAW"  # um "=" digitado não vira fórmula
    assert len(data) == len("30/10/2026 10:45")
