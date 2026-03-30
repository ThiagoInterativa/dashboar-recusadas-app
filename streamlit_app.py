import streamlit as st
import requests
import plotly.express as px
from bs4 import BeautifulSoup
from collections import Counter

st.set_page_config(layout="wide")
st.title("📊 Relatório de Recusas por Técnico")

# ======= FILTROS =======
fila_id = st.text_input("Fila ID", "2812")
data_inicio = st.date_input("Data início")
data_fim = st.date_input("Data fim")

if st.button("Buscar dados"):

    # converte data para string
    data_inicio = str(data_inicio)
    data_fim = str(data_fim)

    url = f"https://pabx.evence.com.br/callcenter/relatorios/recusa-pa?fila_id={fila_id}&data_inicial={data_inicio}&data_final={data_fim}"

    # cookie e headers CORRETOS
    cookie_laravel_session = "eyJpdiI6IkEwTjNlbGhzSDVlZ1lEdTdYTkF5dGc9PSIsInZhbHVlIjoiYUtVUzAzY1Z2djlLNVhuRWEzXC91RlBVZ3gyWkltZnZzMk0wZGtIVmIyZFhUTFdcL0lqS1E2SHhUN0ppcnlUcDRzYmRMZjZiTnBVUnlwUnpMM2pBdkxLUT09IiwibWFjIjoiYmMwMGZmNDU0YmNjNDI1NzdjOTBhNGFlNWU2ZGUwYzlkN2IwYjJkODU0NGRlMzY5ZjJmN2JlYjYxZGMzNDA5ZSJ9"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"laravel_session={cookie_laravel_session}"
    }

    tecnicos = []  # <-- aqui dentro do bloco if, alinhado corretamente

    response = requests.get(url, headers=headers)

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
            response = requests.get(url_pagina, headers=headers)

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
