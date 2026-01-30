# 📊 DataInsight AI: Ultimate Builder

> **Business Intelligence Autônomo impulsionado por Inteligência Artificial Generativa.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![AI](https://img.shields.io/badge/AI-Gemini%20Pro-green)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

## 💡 Sobre o Projeto

O **DataInsight AI** é uma plataforma de Business Intelligence "Self-Service" que revoluciona a forma como analisamos dados. Diferente de dashboards estáticos, esta ferramenta utiliza a **Google Gemini AI** para atuar como um consultor de dados sênior, sugerindo KPIs, gerando gráficos automaticamente e respondendo perguntas complexas sobre a base de dados em linguagem natural.

O sistema possui um **"Motor Híbrido"** de resiliência: se a API de IA falhar, um algoritmo lógico assume a geração dos gráficos, garantindo que o usuário nunca fique sem visualização.

## 🚀 Funcionalidades Principais

* **🤖 Modo Inteligente (AI-Powered):** A IA analisa a estrutura do seu arquivo (CSV/Excel) ou Banco SQL e sugere automaticamente os melhores KPIs e gráficos para o seu contexto de negócio.
* **🎨 Construtor Manual (Builder):** Interface "No-Code" para selecionar entre **+30 tipos de gráficos** (incluindo visuais avançados do Power BI como Waterfall, Funnel, Sankey e Gauge).
* **🩺 Monitor de Saúde dos Dados (Data Health):** Diagnóstico automático de qualidade dos dados, identificando nulidade, duplicatas e confiabilidade da base (feature essencial para Auditoria de Dados).
* **💬 Chat com os Dados:** Um assistente virtual integrado que responde perguntas de negócio gerando gráficos Python/Plotly em tempo real.
* **🔌 Conectividade Híbrida:** Suporte para upload de arquivos locais (`.csv`, `.xlsx`) e conexão direta com bancos de dados **MySQL**.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Frontend:** Streamlit
* **Visualização:** Plotly Express & Graph Objects
* **Inteligência Artificial:** Google Generative AI (Gemini 1.5 Flash / 2.0 / Pro)
* **Banco de Dados:** MySQL Connector
* **Manipulação de Dados:** Pandas

## 📦 Como Executar

### Pré-requisitos
* Python 3.10 ou superior.
* Uma chave de API do Google (Google AI Studio).

### Instalação

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/data-insight-ai.git](https://github.com/SEU-USUARIO/data-insight-ai.git)
   cd data-insight-ai

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt

3. **Configure as credenciais:**
* Crie uma pasta chamada .streamlit na raiz do projeto.
* Crie um arquivo secrets.toml dentro dela.
* Adicione sua chave de API no arquivo:
   ```bash
   GOOGLE_API_KEY = "SUA_CHAVE_AQUI"

4. **Execute a aplicação:**
   ```bash
   streamlit run app.py

5. **🎁 Bônus: Arquivo `requirements.txt`**
   ```bash
   Para que o passo 2 da instalação (`pip install -r requirements.txt`) funcione, crie um arquivo chamado `requirements.txt` na mesma pasta do seu projeto e cole isso dentro:
```text
streamlit
pandas
plotly
google-generativeai
mysql-connector-python
openpyxl
