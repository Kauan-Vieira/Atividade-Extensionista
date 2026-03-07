# 🍃 Curitiba Verde - Mapa Interativo das Áreas Verdes de Curitiba

![Status](https://img.shields.io/badge/Status-Concluído-success)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B)

## 📌 Sobre o Projeto
O **Curitiba Verde** é uma aplicação web interativa desenvolvida como Atividade Extensionista. O objetivo principal é democratizar o acesso à informação sobre a cobertura vegetal (saúde verde) dos bairros de Curitiba e promover o engajamento da Comunidade.

Através de um mapa interativo, os usuários podem visualizar quais regiões possuem maior déficit de árvores e utilizar um formulário integrado para sugerir locais que precisam de novos plantios, podendo inclusive anexar fotos do endereço.

## ✨ Funcionalidades
- **Mapa Interativo:** Visualização geoespacial (Latitude/Longitude) da saúde verde por bairro utilizando Plotly.
- **Painel de Métricas:** Consulta rápida da porcentagem de cobertura vegetal e déficit de árvores filtrada por bairro.
- **Engajamento Comunitário:** Formulário interativo para os cidadãos sugerirem novos plantios, com suporte a upload de imagens.
- **Interface Limpa e Customizada:** Design responsivo focado na Experiência do Usuário (UX) com CSS injetado.

## 🛠️ Tecnologias Utilizadas
- **[Python](https://www.python.org/):** Linguagem base do projeto.
- **[Streamlit](https://streamlit.io/):** Framework para a construção da interface web e deploy.
- **[Pandas](https://pandas.pydata.org/):** Manipulação e tratamento da base de dados (CSV).
- **[Plotly Express](https://plotly.com/python/):** Criação do mapa interativo (Scatter Mapbox).

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

📁 Estrutura de Arquivos

app.py: Código principal da aplicação Streamlit.

style.css: Arquivo de estilização visual da interface.

requirements.txt: Lista de bibliotecas necessárias para rodar o projeto.

src/Dados-Bairros/: Pasta contendo o arquivo bairros_curitiba.csv com a base de dados.

.gitignore: Arquivo para ignorar pastas locais (como o .venv) no controle de versão.

Desenvolvido por Kauan para a Atividade Extensionista Final.
