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
- **Mapa Interativo:** Contorno dos 75 bairros de Curitiba pintado conforme a cobertura de árvores, medida por satélite. Clique em um bairro para ver os dados dele.
- **Evolução da Vegetação:** Gráfico com a vegetação de cada bairro desde 2017, atualizado automaticamente todo ano.
- **Cores Acessíveis:** Três status (Crítico, Alerta e Bom) com cores distinguíveis também por pessoas com daltonismo.
- **Painel de Métricas:** Cobertura de árvores do bairro e quanto a vegetação mudou desde 2017.
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
│       ├── bairros_curitiba.csv       # Cobertura de árvores por bairro (WorldCover)
│       ├── historico_vegetacao.csv    # Vegetação por bairro e ano (MapBiomas)
│       ├── fontes.json                # Fonte e data de cada cálculo
│       └── bairros_curitiba.geojson   # Contorno dos bairros (IPPUC)
├── scripts/coletar_cobertura.py  # Coleta dos dados de satélite
├── tests/test_app.py          # Testes automáticos (pytest + AppTest do Streamlit)
├── style.css                  # Estilização visual da interface
├── .streamlit/config.toml     # Paletas dos temas claro e escuro
├── .streamlit/secrets.toml.example  # Modelo das credenciais da planilha
├── requirements.txt           # Bibliotecas do app (versões fixas)
├── requirements-dev.txt       # Bibliotecas para rodar os testes
└── requirements-coleta.txt    # Bibliotecas do robô de coleta
```

## 📊 Fontes dos Dados
- **Cobertura de árvores (mapa e status):** [ESA WorldCover](https://esa-worldcover.org/) 10 m, ano 2021. É a parte da área de cada bairro classificada como árvores.
- **Evolução da vegetação (2017 em diante):** [MapBiomas](https://brasil.mapbiomas.org/), coleção de 10 m. Inclui árvores, campos, áreas úmidas, silvicultura e pastagens.
- **Contornos dos bairros:** IPPUC, a partir do repositório [geo-curitiba](https://github.com/gustavokira/geo-curitiba). Os contornos foram simplificados para deixar o app mais leve (diferença de área menor que 0,05%).
- **Status:** segue a regra 3-30-300 (Konijnendijk, 2023), que recomenda pelo menos 30% de copa de árvores por bairro.

O arquivo `src/Dados-Bairros/fontes.json` guarda a fonte, as classes usadas e a data de cada cálculo.

### 🤖 Atualização automática dos dados

O workflow `Atualizar dados de vegetação` roda no dia 3 de cada mês e confere se o MapBiomas publicou um ano novo. Se publicou:

1. calcula a vegetação dos 75 bairros com `scripts/coletar_cobertura.py`;
2. confere os números (75 bairros, valores entre 0% e 100%, média plausível e nenhum salto absurdo de um ano para o outro);
3. roda os testes;
4. abre um pull request com os dados novos e um resumo do que mudou.

Nada vai para o ar sem alguém revisar e fazer o merge. Para rodar na mão: aba **Actions > Atualizar dados de vegetação > Run workflow**, ou no computador:

```Bash
pip install -r requirements-coleta.txt
python scripts/coletar_cobertura.py              # anos novos do MapBiomas
python scripts/coletar_cobertura.py --worldcover # recalcula a cobertura de árvores
```

#### Desenvolvido por Kauan para a Atividade Extensionista Final.
