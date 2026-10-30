from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from scripts.coletar_cobertura import validar_ano
from src.dados import (
    CORES_STATUS, carregar_bairros, carregar_contornos, carregar_fontes, carregar_historico,
    definir_status, formatar_pct,
)

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


def test_cobertura_arborea_entre_0_e_100():
    cobertura = carregar_bairros()["cobertura_arborea"]
    assert cobertura.between(0, 100).all()


def test_historico_tem_todos_os_bairros_em_todos_os_anos():
    historico = carregar_historico()
    nomes = set(carregar_bairros()["NOME"])
    for ano, grupo in historico.groupby("ano"):
        assert set(grupo["NOME"]) == nomes, ano
    assert historico["vegetacao"].between(0, 100).all()
    assert sorted(historico["ano"].unique()) == carregar_fontes()["historico_vegetacao"]["anos"]


def test_formatar_pct():
    assert formatar_pct(13.6) == "13,6%"
    assert formatar_pct(-0.25, sinal=True) == "-0,2 p.p."
    assert formatar_pct(1.3, sinal=True) == "+1,3 p.p."


# --- CONFERÊNCIAS DO ROBÔ DE COLETA ---
def test_validar_ano_aceita_dados_atuais():
    historico = carregar_historico()
    ultimo = historico[historico["ano"] == historico["ano"].max()].set_index("NOME")["vegetacao"]
    assert validar_ano(ultimo) == []


def test_validar_ano_recusa_bairro_faltando_e_salto_absurdo():
    import pandas as pd

    anterior = pd.Series([20.0] * 75, index=[f"B{i}" for i in range(75)])
    assert validar_ano(anterior.iloc[:74])  # faltou um bairro
    salto = anterior.copy()
    salto["B0"] = 90.0
    assert any("variação" in p for p in validar_ano(salto, anterior))
    assert any("fora do intervalo" in p for p in validar_ano(anterior.replace(20.0, 120.0)))


@pytest.mark.parametrize("cobertura, status", [
    (0, "Crítico"), (14.9, "Crítico"), (15, "Alerta"), (29.9, "Alerta"), (30, "Bom"), (100, "Bom"),
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
