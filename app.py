import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta, datetime
import time
import re
import json

st.set_page_config(page_title="AirPoint", page_icon="✈️", layout="wide")

# URLs
WEBHOOK_URL = "https://hook.us2.make.com/tofuuriqeniuljwnep5jqctntrtttq6r"
SHEET_ID = "1AYmrD_1zwp4D64rs32zMVYhCjn0c4Ubn9RpeUKfK85o"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
WEBHOOK_MILHAS_URL = "https://hook.us2.make.com/absqlpqrivvd323erxmetebauv5uy3ly"
SHEET_MILHAS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Historico_Milhas"

# Custos de referência R$/1000 milhas
CUSTOS_PROGRAMAS = {
    "Azul": {"min": 12.0, "max": 15.75, "medio": 13.88},
    "TudoAzul": {"min": 12.0, "max": 15.75, "medio": 13.88},
    "Smiles": {"min": 15.0, "max": 15.0, "medio": 15.0},
    "AAdvantage": {"min": 90.0, "max": 90.0, "medio": 90.0},
    "American AAdvantage": {"min": 90.0, "max": 90.0, "medio": 90.0},
    "Avios": {"min": 50.0, "max": 70.0, "medio": 60.0},
    "Iberia Plus": {"min": 50.0, "max": 70.0, "medio": 60.0},
    "TAP": {"min": 35.0, "max": 35.0, "medio": 35.0},
    "TAP Miles&Go": {"min": 35.0, "max": 35.0, "medio": 35.0},
    "LATAM Pass": {"min": 20.0, "max": 25.0, "medio": 22.5},
    "United": {"min": 30.0, "max": 40.0, "medio": 35.0},
    "Delta": {"min": 25.0, "max": 35.0, "medio": 30.0},
    "Flying Blue": {"min": 25.0, "max": 35.0, "medio": 30.0},
}

AIRLINES = {
    "LA": "LATAM", "JJ": "LATAM Brasil", "G3": "Gol", "AD": "Azul",
    "AA": "American Airlines", "UA": "United", "DL": "Delta",
    "LH": "Lufthansa", "AF": "Air France", "BA": "British Airways", "IB": "Iberia",
    "KL": "KLM", "TP": "TAP Portugal", "EK": "Emirates", "QR": "Qatar",
    "CM": "Copa", "AV": "Avianca", "AC": "Air Canada",
}

AIRPORTS = {
    "GRU": {"cidade": "São Paulo", "nome": "Guarulhos", "pais": "Brasil", "metro": "SAO"},
    "CGH": {"cidade": "São Paulo", "nome": "Congonhas", "pais": "Brasil", "metro": "SAO"},
    "VCP": {"cidade": "Campinas", "nome": "Viracopos", "pais": "Brasil", "metro": "SAO"},
    "GIG": {"cidade": "Rio de Janeiro", "nome": "Galeão", "pais": "Brasil", "metro": "RIO"},
    "SDU": {"cidade": "Rio de Janeiro", "nome": "Santos Dumont", "pais": "Brasil", "metro": "RIO"},
    "BSB": {"cidade": "Brasília", "nome": "JK", "pais": "Brasil", "metro": "BSB"},
    "CNF": {"cidade": "Belo Horizonte", "nome": "Confins", "pais": "Brasil", "metro": "BHZ"},
    "SSA": {"cidade": "Salvador", "nome": "Salvador", "pais": "Brasil", "metro": "SSA"},
    "REC": {"cidade": "Recife", "nome": "Guararapes", "pais": "Brasil", "metro": "REC"},
    "FOR": {"cidade": "Fortaleza", "nome": "Fortaleza", "pais": "Brasil", "metro": "FOR"},
    "POA": {"cidade": "Porto Alegre", "nome": "Salgado Filho", "pais": "Brasil", "metro": "POA"},
    "CWB": {"cidade": "Curitiba", "nome": "Afonso Pena", "pais": "Brasil", "metro": "CWB"},
    "FLN": {"cidade": "Florianópolis", "nome": "Hercílio Luz", "pais": "Brasil", "metro": "FLN"},
    "EZE": {"cidade": "Buenos Aires", "nome": "Ezeiza", "pais": "Argentina", "metro": "BUE"},
    "AEP": {"cidade": "Buenos Aires", "nome": "Aeroparque", "pais": "Argentina", "metro": "BUE"},
    "SCL": {"cidade": "Santiago", "nome": "Santiago", "pais": "Chile", "metro": "SCL"},
    "LIM": {"cidade": "Lima", "nome": "Lima", "pais": "Peru", "metro": "LIM"},
    "BOG": {"cidade": "Bogotá", "nome": "El Dorado", "pais": "Colômbia", "metro": "BOG"},
    "JFK": {"cidade": "Nova York", "nome": "JFK", "pais": "EUA", "metro": "NYC"},
    "EWR": {"cidade": "Newark", "nome": "Newark", "pais": "EUA", "metro": "NYC"},
    "LGA": {"cidade": "Nova York", "nome": "LaGuardia", "pais": "EUA", "metro": "NYC"},
    "MIA": {"cidade": "Miami", "nome": "Miami", "pais": "EUA", "metro": "MIA"},
    "FLL": {"cidade": "Fort Lauderdale", "nome": "Fort Lauderdale", "pais": "EUA", "metro": "MIA"},
    "LAX": {"cidade": "Los Angeles", "nome": "LAX", "pais": "EUA", "metro": "LAX"},
    "SFO": {"cidade": "São Francisco", "nome": "SFO", "pais": "EUA", "metro": "SFO"},
    "ORD": {"cidade": "Chicago", "nome": "O'Hare", "pais": "EUA", "metro": "CHI"},
    "DFW": {"cidade": "Dallas", "nome": "DFW", "pais": "EUA", "metro": "DFW"},
    "ATL": {"cidade": "Atlanta", "nome": "Atlanta", "pais": "EUA", "metro": "ATL"},
    "MCO": {"cidade": "Orlando", "nome": "Orlando", "pais": "EUA", "metro": "ORL"},
    "PTY": {"cidade": "Cidade do Panamá", "nome": "Tocumen", "pais": "Panamá", "metro": "PTY"},
    "LHR": {"cidade": "Londres", "nome": "Heathrow", "pais": "Reino Unido", "metro": "LON"},
    "LGW": {"cidade": "Londres", "nome": "Gatwick", "pais": "Reino Unido", "metro": "LON"},
    "CDG": {"cidade": "Paris", "nome": "CDG", "pais": "França", "metro": "PAR"},
    "ORY": {"cidade": "Paris", "nome": "Orly", "pais": "França", "metro": "PAR"},
    "FRA": {"cidade": "Frankfurt", "nome": "Frankfurt", "pais": "Alemanha", "metro": "FRA"},
    "AMS": {"cidade": "Amsterdã", "nome": "Schiphol", "pais": "Holanda", "metro": "AMS"},
    "MAD": {"cidade": "Madri", "nome": "Barajas", "pais": "Espanha", "metro": "MAD"},
    "BCN": {"cidade": "Barcelona", "nome": "El Prat", "pais": "Espanha", "metro": "BCN"},
    "FCO": {"cidade": "Roma", "nome": "Fiumicino", "pais": "Itália", "metro": "ROM"},
    "LIS": {"cidade": "Lisboa", "nome": "Lisboa", "pais": "Portugal", "metro": "LIS"},
    "OPO": {"cidade": "Porto", "nome": "Porto", "pais": "Portugal", "metro": "OPO"},
    "DXB": {"cidade": "Dubai", "nome": "Dubai", "pais": "Emirados", "metro": "DXB"},
    "DOH": {"cidade": "Doha", "nome": "Doha", "pais": "Catar", "metro": "DOH"},
}

METRO_CODES = {
    "SAO": {"nome": "São Paulo (Todos)", "aeroportos": ["GRU", "CGH", "VCP"]},
    "RIO": {"nome": "Rio de Janeiro (Todos)", "aeroportos": ["GIG", "SDU"]},
    "BUE": {"nome": "Buenos Aires (Todos)", "aeroportos": ["EZE", "AEP"]},
    "NYC": {"nome": "Nova York (Todos)", "aeroportos": ["JFK", "EWR", "LGA"]},
    "LON": {"nome": "Londres (Todos)", "aeroportos": ["LHR", "LGW"]},
    "PAR": {"nome": "Paris (Todos)", "aeroportos": ["CDG", "ORY"]},
}

def expand_airport_code(code):
    code = code.upper().strip()
    if code in METRO_CODES:
        return METRO_CODES[code]['aeroportos']
    return [code]

def search_airports(query):
    query = query.lower().strip()
    results = []
    for code, info in METRO_CODES.items():
        if query in code.lower() or query in info['nome'].lower():
            results.append({"codigo": code, "cidade": info['nome'], "nome": f"Inclui: {', '.join(info['aeroportos'])}", "pais": "", "tipo": "metro"})
    for code, info in AIRPORTS.items():
        if query in code.lower() or query in info["cidade"].lower() or query in info["pais"].lower():
            results.append({"codigo": code, "cidade": info["cidade"], "nome": info["nome"], "pais": info["pais"], "tipo": "aeroporto"})
    return results[:15]

def get_airline_name(code):
    return AIRLINES.get(str(code).strip(), str(code)) if not pd.isna(code) else code

def get_custo_programa(programa):
    for key, value in CUSTOS_PROGRAMAS.items():
        if key.lower() in programa.lower() or programa.lower() in key.lower():
            return value
    return {"min": 20.0, "max": 30.0, "medio": 25.0}

def calcular_custo_milhas(milhas, programa):
    return (milhas / 1000) * get_custo_programa(programa)['medio']

@st.cache_data(ttl=30)
def load_flight_data():
    try:
        df = pd.read_csv(SHEET_URL)
        num_cols = len(df.columns)
        if num_cols >= 12:
            df.columns = ['Data Busca', 'Origem', 'Destino', 'Data Voo', 'Companhia', 'Num Voo', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas'][:num_cols]
        elif num_cols >= 11:
            df.columns = ['Data Busca', 'Origem', 'Destino', 'Data Voo', 'Companhia', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas'][:num_cols]
            df['Num Voo'] = ''
        else:
            return None
        df['Preço BRL'] = pd.to_numeric(df['Preço BRL'], errors='coerce')
        df['Paradas'] = pd.to_numeric(df['Paradas'], errors='coerce').fillna(0).astype(int)
        df['Companhia Nome'] = df['Companhia'].apply(get_airline_name)
        return df
    except Exception as e:
        return None

@st.cache_data(ttl=60)
def load_historico_milhas():
    try:
        return pd.read_csv(SHEET_MILHAS_URL)
    except:
        return None

def format_duration(d):
    try:
        return str(d).replace('PT', '').replace('H', 'h ').replace('M', 'min')
    except:
        return d

def format_time(t):
    try:
        return str(t).split('T')[1][:5] if 'T' in str(t) else '-'
    except:
        return '-'

def format_stops(s):
    try:
        s = int(float(s))
        return "Direto" if s == 0 else f"{s} parada{'s' if s > 1 else ''}"
    except:
        return str(s)

def parse_seats_aero_table(text):
    results = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or 'Programa' in line or '---' in line:
            continue
        result = {}
        
        # Milhas
        m = re.search(r'(\d{1,3}[.,]\d{3}|\d{2,6})', line)
        if m:
            try:
                result['milhas'] = int(m.group(1).replace('.', '').replace(',', ''))
            except:
                pass
        
        # Programa
        for prog in ['American AAdvantage', 'AAdvantage', 'Smiles', 'Azul', 'TudoAzul', 'LATAM Pass', 'TAP', 'Iberia Plus', 'Avios', 'United', 'Delta', 'Flying Blue']:
            if prog.lower() in line.lower():
                result['programa'] = prog
                break
        
        # Data
        d = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})', line)
        if d:
            result['data'] = d.group(1)
        
        # Voo
        f = re.search(r'\b([A-Z]{2}\d{1,4})\b', line)
        if f:
            result['num_voo'] = f.group(1)
        
        # Classe
        if re.search(r'\beconomy\b', line, re.I):
            result['classe'] = 'Economy'
        elif re.search(r'\bbusiness\b', line, re.I):
            result['classe'] = 'Business'
        elif re.search(r'\bfirst\b', line, re.I):
            result['classe'] = 'First'
        
        # Companhia
        for code, name in AIRLINES.items():
            if name.lower() in line.lower():
                result['companhia'] = name
                break
        
        # Paradas
        if re.search(r'\bdireto\b', line, re.I):
            result['paradas'] = 'Direto'
        elif re.search(r'\d+\s*parada', line, re.I):
            result['paradas'] = '1+ parada'
        
        if 'milhas' in result:
            results.append(result)
    return results

# Session state
if 'ultima_busca' not in st.session_state:
    st.session_state.ultima_busca = None
if 'resultados_milhas' not in st.session_state:
    st.session_state.resultados_milhas = []

# Interface
st.title("✈️ AirPoint - Comparador de Voos")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔍 Buscar Voos", "📊 Resultados", "🎫 Buscar Milhas", "🎯 Comparador", "📜 Histórico", "🛫 Aeroportos"])

# TAB 1: BUSCAR VOOS
with tab1:
    st.subheader("Buscar Voos")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Origem**")
        modo_origem = st.radio("Modo:", ["Código IATA", "Área Metropolitana"], key="modo_orig", horizontal=True)
        
        if modo_origem == "Área Metropolitana":
            metros_opcoes = [f"{k} - {v['nome']}" for k, v in METRO_CODES.items()]
            metro_sel = st.selectbox("Selecione a região:", metros_opcoes, key="metro_orig")
            if metro_sel:
                metro_code = metro_sel.split(' - ')[0]
                origens = METRO_CODES[metro_code]['aeroportos']
                st.success(f"✅ Aeroportos: {', '.join(origens)}")
            else:
                origens = ["GRU"]
        else:
            busca_origem = st.text_input("🔎 Buscar aeroporto:", placeholder="Ex: GRU, São Paulo, Miami", key="busca_orig")
            origens = []
            if busca_origem:
                res = search_airports(busca_origem)
                # Filtra só aeroportos (não metros)
                res_aeroportos = [r for r in res if r['tipo'] == 'aeroporto']
                if res_aeroportos:
                    opts = [f"{r['codigo']} - {r['cidade']} ({r['pais']})" for r in res_aeroportos]
                    sel = st.multiselect("Selecione (máx 2):", opts, max_selections=2, key="so")
                    for s in sel:
                        code = s.split(' - ')[0]
                        origens.append(code)
            if not origens:
                origens = ["GRU"]
            st.caption(f"Selecionados: {', '.join(origens)}")
    
    with col2:
        st.markdown("**Destino**")
        modo_destino = st.radio("Modo:", ["Código IATA", "Área Metropolitana"], key="modo_dest", horizontal=True)
        
        if modo_destino == "Área Metropolitana":
            metros_opcoes = [f"{k} - {v['nome']}" for k, v in METRO_CODES.items()]
            metro_sel = st.selectbox("Selecione a região:", metros_opcoes, key="metro_dest")
            if metro_sel:
                metro_code = metro_sel.split(' - ')[0]
                destinos = METRO_CODES[metro_code]['aeroportos']
                st.success(f"✅ Aeroportos: {', '.join(destinos)}")
            else:
                destinos = ["MIA"]
        else:
            busca_destino = st.text_input("🔎 Buscar aeroporto:", placeholder="Ex: MIA, Miami, Lisboa", key="busca_dest")
            destinos = []
            if busca_destino:
                res = search_airports(busca_destino)
                res_aeroportos = [r for r in res if r['tipo'] == 'aeroporto']
                if res_aeroportos:
                    opts = [f"{r['codigo']} - {r['cidade']} ({r['pais']})" for r in res_aeroportos]
                    sel = st.multiselect("Selecione (máx 2):", opts, max_selections=2, key="sd")
                    for s in sel:
                        code = s.split(' - ')[0]
                        destinos.append(code)
            if not destinos:
                destinos = ["MIA"]
            st.caption(f"Selecionados: {', '.join(destinos)}")
    
    st.divider()
    
    col3, col4, col5 = st.columns(3)
    with col3:
        data_inicio = st.date_input("📅 Data Inicial", value=date.today() + timedelta(days=30), min_value=date.today() + timedelta(days=1), key="data_ini")
    with col4:
        data_fim = st.date_input("📅 Data Final", value=data_inicio, min_value=data_inicio, max_value=data_inicio + timedelta(days=30), key="data_fim", help="Máximo 30 dias de período")
    with col5:
        tipo_voo = st.selectbox("✈️ Tipo", ["Todos", "Somente Diretos", "Com Conexão"])
    
    col6, col7 = st.columns(2)
    with col6:
        adultos = st.number_input("👤 Adultos", min_value=1, max_value=9, value=1)
    with col7:
        # Calcula número de dias
        num_dias = (data_fim - data_inicio).days + 1
        st.info(f"📆 Período: **{num_dias} dia(s)** ({data_inicio.strftime('%d/%m')} a {data_fim.strftime('%d/%m')})")
    
    # Aviso de muitas buscas
    total_buscas = len(origens) * len(destinos) * num_dias
    if total_buscas > 10:
        st.warning(f"⚠️ Esta busca fará **{total_buscas} requisições**. Pode demorar alguns minutos.")
    
    if st.button("🔍 Buscar", type="primary", use_container_width=True):
        if not origens:
            origens = ["GRU"]
        if not destinos:
            destinos = ["MIA"]
        
        # Gera lista de datas
        datas_busca = []
        data_atual = data_inicio
        while data_atual <= data_fim:
            datas_busca.append(data_atual)
            data_atual += timedelta(days=1)
        
        st.session_state.ultima_busca = {
            'origens': origens, 'destinos': destinos,
            'data_inicio': data_inicio.strftime("%Y-%m-%d"),
            'data_fim': data_fim.strftime("%Y-%m-%d"),
            'datas': [d.strftime("%Y-%m-%d") for d in datas_busca],
            'data_display': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}" if num_dias > 1 else data_inicio.strftime("%d/%m/%Y"),
            'paradas': tipo_voo
        }
        
        prog = st.progress(0)
        status = st.empty()
        sucesso = 0
        total = len(origens) * len(destinos) * len(datas_busca)
        atual = 0
        
        for data_busca in datas_busca:
            for orig in origens:
                for dest in destinos:
                    if orig != dest:
                        atual += 1
                        status.text(f"Buscando {orig} → {dest} em {data_busca.strftime('%d/%m')}... ({atual}/{total})")
                        try:
                            params = {"origin": orig, "destination": dest, "date": data_busca.strftime("%Y-%m-%d"), "adults": adultos, "nonstop": "true" if tipo_voo == "Somente Diretos" else "false"}
                            r = requests.get(WEBHOOK_URL, params=params, timeout=60)
                            if r.status_code == 200:
                                sucesso += 1
                        except:
                            pass
                        prog.progress(atual / total)
        
        status.empty()
        if sucesso > 0:
            st.success(f"✅ {sucesso} busca(s) realizada(s)!")
            with st.spinner("Aguardando processamento..."):
                time.sleep(5)
            st.cache_data.clear()
            st.info("👆 Veja os resultados na aba **Resultados**")

# TAB 2: RESULTADOS
with tab2:
    st.subheader("📊 Resultados")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        debug_mode = st.checkbox("🔧 Modo Debug", value=False)
    
    if st.session_state.ultima_busca:
        b = st.session_state.ultima_busca
        st.info(f"🔍 Busca: **{', '.join(b['origens'])} → {', '.join(b['destinos'])}** | Período: **{b['data_display']}**")
        
        if debug_mode:
            with st.expander("📋 Dados da Última Busca (Debug)"):
                st.json(b)
    else:
        st.warning("⚠️ Nenhuma busca realizada. Vá para a aba 'Buscar Voos' primeiro.")
        st.stop()
    
    # Carrega dados
    df = load_flight_data()
    
    if debug_mode:
        with st.expander("📋 Dados da Planilha (Debug)"):
            if df is not None:
                st.write(f"Total de linhas: {len(df)}")
                st.write(f"Colunas: {list(df.columns)}")
                st.write("Primeiras 5 linhas:")
                st.dataframe(df.head())
                st.write("Origens únicas:", df['Origem'].unique().tolist() if 'Origem' in df.columns else "N/A")
                st.write("Destinos únicos:", df['Destino'].unique().tolist() if 'Destino' in df.columns else "N/A")
                st.write("Datas únicas:", df['Data Voo'].unique().tolist() if 'Data Voo' in df.columns else "N/A")
            else:
                st.error("DataFrame é None - erro ao carregar planilha")
    
    if df is None:
        st.error("❌ Erro ao carregar dados da planilha. Verifique a conexão.")
        st.stop()
    
    if len(df) == 0:
        st.warning("⚠️ Planilha vazia. Faça uma busca primeiro.")
        st.stop()
    
    # Aplica filtros
    df_f = df.copy()
    
    # Filtro 1: Origem
    df_f = df_f[df_f['Origem'].isin(b['origens'])]
    if debug_mode:
        st.write(f"Após filtro origem ({b['origens']}): {len(df_f)} linhas")
    
    # Filtro 2: Destino
    df_f = df_f[df_f['Destino'].isin(b['destinos'])]
    if debug_mode:
        st.write(f"Após filtro destino ({b['destinos']}): {len(df_f)} linhas")
    
    # Filtro 3: Datas
    if 'datas' in b and b['datas']:
        df_f = df_f[df_f['Data Voo'].isin(b['datas'])]
        if debug_mode:
            st.write(f"Após filtro datas ({b['datas']}): {len(df_f)} linhas")
    
    # Filtro 4: Paradas
    if b.get('paradas') == "Somente Diretos":
        df_f = df_f[df_f['Paradas'] == 0]
        if debug_mode:
            st.write(f"Após filtro diretos: {len(df_f)} linhas")
    elif b.get('paradas') == "Com Conexão":
        df_f = df_f[df_f['Paradas'] > 0]
        if debug_mode:
            st.write(f"Após filtro conexões: {len(df_f)} linhas")
    
    st.divider()
    
    if len(df_f) == 0:
        st.warning("⚠️ Nenhum voo encontrado para os critérios selecionados.")
        
        # Sugestões
        st.markdown("**Possíveis causas:**")
        st.markdown("- A busca ainda não foi processada (aguarde alguns segundos e clique em 'Atualizar')")
        st.markdown("- Os dados ainda não chegaram na planilha")
        st.markdown("- Os filtros de origem/destino/data não correspondem aos dados")
        
        if debug_mode:
            st.markdown("**Dados disponíveis na planilha:**")
            st.write("Rotas disponíveis:")
            if len(df) > 0:
                rotas = df.groupby(['Origem', 'Destino', 'Data Voo']).size().reset_index(name='Voos')
                st.dataframe(rotas)
    else:
        # Filtro por data específica (se período)
        if 'datas' in b and len(b['datas']) > 1:
            datas_disponiveis = sorted(df_f['Data Voo'].unique().tolist())
            if datas_disponiveis:
                data_selecionada = st.selectbox(
                    "📅 Filtrar por data:",
                    ["Todas"] + datas_disponiveis,
                    key="filtro_data_resultado"
                )
                if data_selecionada != "Todas":
                    df_f = df_f[df_f['Data Voo'] == data_selecionada]
        
        st.divider()
        
        # Melhores opções por classe
        st.markdown("### 🏆 Melhores Opções")
        for classe in df_f['Classe'].unique():
            df_c = df_f[df_f['Classe'] == classe]
            if len(df_c) > 0:
                melhor = df_c.loc[df_c['Preço BRL'].idxmin()]
                st.markdown(f"#### {classe}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("💰 Menor Preço", f"R$ {melhor['Preço BRL']:,.2f}")
                with col2:
                    data_voo_str = str(melhor['Data Voo'])
                    try:
                        data_voo_fmt = datetime.strptime(data_voo_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except:
                        data_voo_fmt = data_voo_str
                    st.metric("📅 Data", data_voo_fmt)
                with col3:
                    st.metric("✈️ Voo", f"{melhor['Companhia Nome']} {melhor.get('Num Voo', '')}")
                st.caption(f"Rota: {melhor['Origem']} → {melhor['Destino']} | {format_stops(melhor['Paradas'])}")
        
        st.divider()
        
        # Tabela completa
        st.markdown("### 📋 Todos os Voos")
        cols = [c for c in ['Origem', 'Destino', 'Data Voo', 'Companhia Nome', 'Num Voo', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Paradas'] if c in df_f.columns]
        df_d = df_f[cols].copy()
        
        # Formata colunas
        if 'Data Voo' in df_d.columns:
            df_d['Data Voo'] = df_d['Data Voo'].apply(lambda x: datetime.strptime(str(x), "%Y-%m-%d").strftime("%d/%m") if x else x)
        df_d['Preço BRL'] = df_d['Preço BRL'].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "N/A")
        df_d['Duração'] = df_d['Duração'].apply(format_duration)
        df_d['Partida'] = df_d['Partida'].apply(format_time)
        df_d['Paradas'] = df_d['Paradas'].apply(format_stops)
        
        st.dataframe(df_d, use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df_f)} voos encontrados")

# TAB 3: BUSCAR MILHAS
with tab3:
    st.subheader("🎫 Buscar Milhas")
    
    if st.session_state.ultima_busca:
        b = st.session_state.ultima_busca
        st.success(f"📍 **{b['origens'][0]} → {b['destinos'][0]}** | Período: **{b['data_display']}**")
        orig_m, dest_m = b['origens'][0], b['destinos'][0]
        # Usa período se disponível
        if 'data_inicio' in b and 'data_fim' in b:
            data_m = f"{datetime.strptime(b['data_inicio'], '%Y-%m-%d').strftime('%d/%m/%Y')} a {datetime.strptime(b['data_fim'], '%Y-%m-%d').strftime('%d/%m/%Y')}"
        else:
            data_m = b['data_display']
    else:
        orig_m, dest_m = "GRU", "MIA"
        data_m = (date.today() + timedelta(30)).strftime("%d/%m/%Y")
    
    col1, col2 = st.columns(2)
    with col1:
        award_only = st.checkbox("🎯 Somente Award", value=True)
    with col2:
        inc_conex = st.checkbox("🔄 Incluir conexões", value=True)
    
    cabines = st.multiselect("Cabines", ["Economy", "Business", "First"], default=["Economy", "Business"])
    progs = st.multiselect("Programas", ["Smiles", "AAdvantage", "Azul", "TAP", "Avios"], default=["Smiles", "AAdvantage", "Azul"])
    
    orig_nome = AIRPORTS.get(orig_m, {}).get("cidade", orig_m)
    dest_nome = AIRPORTS.get(dest_m, {}).get("cidade", dest_m)
    
    prompt = f"""Busque award de {orig_m} ({orig_nome}) para {dest_m} ({dest_nome}).
Período: {data_m}
Cabines: {', '.join(cabines)}
{"Somente Award" if award_only else ""}
{"Somente diretos" if not inc_conex else ""}
Programas: {', '.join(progs)}

Tabela: Programa | Data | Nº Voo | Milhas | Classe | Companhia | Direto/Conexão | Assentos
Ordene por milhas."""

    st.code(prompt)
    st.markdown('<a href="https://seats.aero/assistant" target="_blank"><button style="background:#FF6B6B;color:white;padding:10px 20px;border:none;border-radius:5px;width:100%">🚀 Abrir Seats.aero</button></a>', unsafe_allow_html=True)
    
    st.divider()
    resultado = st.text_area("📋 Cole o resultado:", height=200)
    
    if st.button("🔍 Processar", type="primary", use_container_width=True) and resultado:
        res = parse_seats_aero_table(resultado)
        if res:
            st.session_state.resultados_milhas = res
            st.success(f"✅ {len(res)} opções!")
            
            df_m = pd.DataFrame(res)
            if 'milhas' in df_m.columns:
                df_m['Custo Est.'] = df_m.apply(lambda r: f"R$ {calcular_custo_milhas(r['milhas'], r.get('programa', '')):,.2f}", axis=1)
            st.dataframe(df_m, use_container_width=True, hide_index=True)
            
            # Comparação
            df_cash = load_flight_data()
            if df_cash is not None and st.session_state.ultima_busca:
                b = st.session_state.ultima_busca
                df_r = df_cash[(df_cash['Origem'].isin(b['origens'])) & (df_cash['Destino'].isin(b['destinos']))]
                if len(df_r) > 0:
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 💵 Dinheiro")
                        st.metric("Menor", f"R$ {df_r['Preço BRL'].min():,.2f}")
                    with col2:
                        st.markdown("#### 🎫 Milhas")
                        melhor = min(res, key=lambda x: x.get('milhas', 999999))
                        custo = calcular_custo_milhas(melhor.get('milhas', 0), melhor.get('programa', ''))
                        st.metric(melhor.get('programa', ''), f"{melhor.get('milhas', 0):,} mi", f"≈ R$ {custo:,.2f}")
                    
                    eco = df_r['Preço BRL'].min() - custo
                    if eco > 0:
                        st.success(f"✅ Milhas economizam **R$ {eco:,.2f}**")
                    else:
                        st.warning(f"💵 Dinheiro é **R$ {abs(eco):,.2f}** mais barato")
            
            # Salva
            try:
                payload = {"data_busca": datetime.now().strftime("%Y-%m-%d %H:%M"), "origem": orig_m, "destino": dest_m, "periodo": data_m, "quantidade_opcoes": len(res), "melhor_milhas": min([r.get('milhas', 999999) for r in res]), "melhor_programa": min(res, key=lambda x: x.get('milhas', 999999)).get('programa', ''), "resultados_json": json.dumps(res, ensure_ascii=False)}
                requests.post(WEBHOOK_MILHAS_URL, json=payload, timeout=10)
            except:
                pass
        else:
            st.warning("Não extraiu dados")
    
    with st.expander("📊 Custos Referência"):
        st.dataframe(pd.DataFrame([{"Programa": k, "R$/1000mi": f"R$ {v['medio']:.2f}"} for k, v in CUSTOS_PROGRAMAS.items()]), hide_index=True)

# TAB 4: COMPARADOR
with tab4:
    st.subheader("🎯 Comparador")
    col1, col2 = st.columns(2)
    with col1:
        preco = st.number_input("💵 Preço (R$)", value=3000.0, step=100.0)
    with col2:
        prog = st.selectbox("Programa", list(CUSTOS_PROGRAMAS.keys()))
        milhas = st.number_input("Milhas", value=30000, step=1000)
    
    if st.button("📊 Comparar", use_container_width=True):
        custo = calcular_custo_milhas(milhas, prog)
        eco = preco - custo
        col1, col2 = st.columns(2)
        col1.metric("💵", f"R$ {preco:,.2f}")
        col2.metric("🎫", f"R$ {custo:,.2f}", f"{milhas:,} mi")
        if eco > 0:
            st.success(f"✅ Milhas! Economia R$ {eco:,.2f}")
        else:
            st.warning("💵 Pague em dinheiro")

# TAB 5: HISTÓRICO
with tab5:
    st.subheader("📜 Histórico")
    df_h = load_historico_milhas()
    if df_h is not None and len(df_h) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            fo = st.selectbox("Origem", ['Todas'] + sorted(df_h['Origem'].unique().tolist()) if 'Origem' in df_h.columns else ['Todas'])
        with col2:
            fd = st.selectbox("Destino", ['Todos'] + sorted(df_h['Destino'].unique().tolist()) if 'Destino' in df_h.columns else ['Todos'])
        with col3:
            fp = st.selectbox("Data", ['Todas'] + sorted(df_h['Periodo'].unique().tolist()) if 'Periodo' in df_h.columns else ['Todas'])
        
        df_hf = df_h.copy()
        if fo != 'Todas' and 'Origem' in df_hf.columns:
            df_hf = df_hf[df_hf['Origem'] == fo]
        if fd != 'Todos' and 'Destino' in df_hf.columns:
            df_hf = df_hf[df_hf['Destino'] == fd]
        if fp != 'Todas' and 'Periodo' in df_hf.columns:
            df_hf = df_hf[df_hf['Periodo'] == fp]
        st.dataframe(df_hf, use_container_width=True, hide_index=True)
    else:
        st.info("Sem histórico")

# TAB 6: AEROPORTOS
with tab6:
    st.subheader("🛫 Aeroportos")
    q = st.text_input("Buscar:", placeholder="Ex: São Paulo, NYC")
    if q:
        r = search_airports(q)
        if r:
            st.dataframe(pd.DataFrame(r), hide_index=True)
    with st.expander("Códigos Metro"):
        st.markdown("|Código|Aeroportos|\n|---|---|\n|SAO|GRU,CGH,VCP|\n|RIO|GIG,SDU|\n|NYC|JFK,EWR,LGA|\n|LON|LHR,LGW|")

st.divider()
st.markdown("<div style='text-align:center;color:gray;font-size:12px'>AirPoint © 2025</div>", unsafe_allow_html=True)
