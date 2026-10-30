# 🍃 Curitiba Verde - Mapa Interativo das Áreas Verdes de Curitiba

![Status](https://img.shields.io/badge/Status-Concluído-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Testes](https://github.com/Kauan-Vieira/Atividade-Extensionista/actions/workflows/testes.yml/badge.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B)

## 📌 Sobre o Projeto
O **Curitiba Verde** é uma aplicação web interativa desenvolvida como Atividade Extensionista. O objetivo principal é democratizar o acesso à informação sobre a cobertura vegetal (saúde verde) dos bairros de Curitiba e promover o engajamento da Comunidade.

🌐 **Acesse o app publicado:** https://curitiba-verde.streamlit.app/

Através de um mapa interativo, os usuários podem visualizar quais regiões possuem maior déficit de árvores e utilizar um formulário integrado para sugerir locais que precisam de novos plantios.

## ✨ Funcionalidades
- **Mapa Interativo:** Contorno dos 75 bairros de Curitiba pintado conforme a cobertura vegetal. Clique em um bairro para ver os dados dele.
- **Cores Acessíveis:** Três status (Crítico, Alerta e Bom) com cores distinguíveis também por pessoas com daltonismo.
- **Painel de Métricas:** Consulta rápida da porcentagem de cobertura vegetal e déficit de árvores filtrada por bairro.
- **Engajamento Comunitário:** Formulário para os cidadãos sugerirem novos plantios. As sugestões ficam salvas numa planilha do Google Sheets.
- **Temas Claro e Escuro:** O visual se adapta ao tema escolhido em ⋮ > Settings > Theme.

## 🛠️ Tecnologias Utilizadas
- **[Python](https://www.python.org/):** Linguagem base do projeto.
- **[Streamlit](https://streamlit.io/):** Framework para a construção da interface web e deploy.
- **[Pandas](https://pandas.pydata.org/):** Manipulação e tratamento da base de dados (CSV).
- **[Plotly Express](https://plotly.com/python/):** Criação do mapa interativo (Choropleth Map).

## 🚀 Como rodar o projeto localmente

Siga os passos abaixo para executar a aplicação na sua máquina:

1. **Clone este repositório:**

```bash
git clone https://github.com/Kauan-Vieira/Atividade-extensionista.git
```
Acesse a pasta do projeto:

```Bash
cd Atividade-extensionista
```
Crie e ative um ambiente virtual (Windows):

```Bash
python -m venv .venv
.\.venv\Scripts\activate
```
Instale as dependências:

```Bash
pip install -r requirements.txt
```
Execute a aplicação:

```Bash
streamlit run app.py
```

### 📝 Configurando a planilha de sugestões (Google Sheets)

Sem esta configuração o app funciona normalmente, mas o formulário avisa que o envio ainda não está configurado.

1. No [Google Cloud Console](https://console.cloud.google.com/), crie um projeto e ative a **Google Sheets API**.
2. Em **IAM e administrador > Contas de serviço**, crie uma conta de serviço. Na aba **Chaves**, adicione uma chave do tipo **JSON** e baixe o arquivo.
3. Crie uma planilha no Google Sheets e **compartilhe** com o e-mail da conta de serviço (o `client_email` do JSON), com permissão de **Editor**.
4. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha com o link da planilha e os dados do JSON.
5. No Streamlit Cloud, cole o mesmo conteúdo em **Manage app > Settings > Secrets**.

O arquivo `secrets.toml` está no `.gitignore`: **nunca** envie as credenciais para o GitHub.

### 🧪 Rodando os testes

```Bash
pip install -r requirements-dev.txt
pytest
```
Os testes também rodam automaticamente no GitHub Actions a cada push e pull request.

## 📁 Estrutura de Arquivos

```
├── app.py                     # Entrada do app: configuração, CSS e navegação entre páginas
├── paginas/
│   ├── mapa.py                # Mapa dos bairros, seleção e cards de métricas
│   ├── sugestoes.py           # Formulário de sugestão de plantio
│   └── sobre.py               # Sobre o projeto, legenda das cores e fontes
├── src/
│   ├── dados.py               # Leitura dos dados, status e paleta de cores
│   ├── planilha.py            # Gravação das sugestões no Google Sheets
│   └── Dados-Bairros/
│       ├── bairros_curitiba.csv       # Cobertura vegetal por bairro
│       └── bairros_curitiba.geojson   # Contorno dos bairros (IPPUC)
├── tests/test_app.py          # Testes automáticos (pytest + AppTest do Streamlit)
├── style.css                  # Estilização visual da interface
├── .streamlit/config.toml     # Paletas dos temas claro e escuro
├── .streamlit/secrets.toml.example  # Modelo das credenciais da planilha
├── requirements.txt           # Bibliotecas do app (versões fixas)
└── requirements-dev.txt       # Bibliotecas para rodar os testes
```

## 📊 Fontes dos Dados
- **Contornos dos bairros:** IPPUC, a partir do repositório [geo-curitiba](https://github.com/gustavokira/geo-curitiba). Os contornos foram simplificados para deixar o app mais leve (diferença de área menor que 0,05%).

#### Desenvolvido por Kauan para a Atividade Extensionista Final.
