import streamlit as st
import requests
import plotly.express as px
from bs4 import BeautifulSoup
from collections import Counter

st.set_page_config(layout="wide")
st.title("📊 Relatório de Recusas por Técnico")

if "session_pabx" not in st.session_state:
    st.session_state.session_pabx = login_pabx()
    
# ======= FILTROS =======
fila_id = st.text_input("Fila ID", "2812")
data_inicio = st.date_input("Data início")
data_fim = st.date_input("Data fim")

if st.button("Buscar dados"):

    # converte data para string
    data_inicio = str(data_inicio)
    data_fim = str(data_fim)

    url = f"https://pabx.evence.com.br/callcenter/relatorios/recusa-pa?fila_id={fila_id}&data_inicial={data_inicio}&data_final={data_fim}"

    #login
    login_url = "https://pabx.evence.com.br/login"

email = suporte@interativanet.com.br
senha = smk03657

def login_pabx():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    
    try:
        r = session.get(login_url)
        soup = BeautifulSoup(r.text, "html.parser")

        csrf = soup.find("input", {"name": "_token"})
        if not csrf:
            st.error("Erro ao pegar token CSRF")
            return None

        payload = {
            "login": email,
            "senha": senha,
            "_token": csrf["value"]
        }

        response = session.post(login_url, data=payload)

        if response.url == login_url:
            st.error("Login falhou")
            return None

        return session

    except Exception as e:
        st.error(f"Erro no login: {e}")
        return None
        

    tecnicos = []  # <-- aqui dentro do bloco if, alinhado corretamente

session = st.session_state.session_pabx

if not session:
    st.error("Sessão inválida")
    st.stop()

response = session.get(url)
if "login" in response.url:
    session = login_pabx()
    st.session_state.session_pabx = session
    response = session.get(url)

    if response.status_code != 200:
        st.error("Erro ao acessar relatório")
    else:
        soup = BeautifulSoup(response.text, "html.parser")

        # pegar páginas
        ultima_pagina = 1
        paginacao = soup.find("ul", class_="pagination")

        if paginacao:
            paginas = paginacao.find_all("a")
            numeros = []

            for p in paginas:
                try:
                    numeros.append(int(p.text.strip()))
                except:
                    pass

            if numeros:
                ultima_pagina = max(numeros)

        # loop páginas
        for page in range(1, ultima_pagina + 1):
            url_pagina = f"{url}&page={page}"
            response = session.get(url_pagina)
            soup = BeautifulSoup(response.text, "html.parser")
            tabela = soup.find("table")

            if not tabela:
                continue

            linhas = tabela.find("tbody").find_all("tr")

            for linha in linhas:
                colunas = linha.find_all("td")
                if len(colunas) >= 3:
                    tecnico = colunas[2].text.strip()
                    tecnicos.append(tecnico)

        contagem = dict(Counter(tecnicos))

        # ===== CARDS =====
        st.subheader("Resumo por técnico")

        cols = st.columns(4)
        i = 0
        for t, q in contagem.items():
            cols[i % 4].metric(t, q)
            i += 1

        # ===== GRÁFICO =====
        nomes = list(contagem.keys())
        recusas = list(contagem.values())

        fig = px.pie(
            names=nomes,
            values=recusas,
            title="Proporção de Recusas"
        )

        st.plotly_chart(fig, use_container_width=True)
