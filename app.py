import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
import time

# Configuração da página
st.set_page_config(
    page_title="AirPoint - Busca de Voos",
    page_icon="✈️",
    layout="wide"
)

# URLs
WEBHOOK_URL = "https://hook.us2.make.com/tofuuriqeniuljwnep5jqctntrtttq6r"
SHEET_ID = "1AYmrD_1zwp4D64rs32zMVYhCjn0c4Ubn9RpeUKfK85o"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Tabela de companhias aéreas
AIRLINES = {
    # América do Sul
    "LA": "LATAM Airlines",
    "JJ": "LATAM Brasil",
    "G3": "Gol",
    "AD": "Azul",
    "AV": "Avianca",
    "AR": "Aerolíneas Argentinas",
    "CM": "Copa Airlines",
    "H2": "Sky Airline",
    # América do Norte
    "AA": "American Airlines",
    "UA": "United Airlines",
    "DL": "Delta Air Lines",
    "WN": "Southwest Airlines",
    "B6": "JetBlue",
    "AS": "Alaska Airlines",
    "NK": "Spirit Airlines",
    "F9": "Frontier Airlines",
    "AC": "Air Canada",
    "WS": "WestJet",
    "AM": "Aeroméxico",
    "VB": "VivaAerobus",
    # Europa
    "LH": "Lufthansa",
    "AF": "Air France",
    "BA": "British Airways",
    "IB": "Iberia",
    "KL": "KLM",
    "AZ": "ITA Airways",
    "TP": "TAP Portugal",
    "LX": "Swiss",
    "OS": "Austrian Airlines",
    "SK": "SAS Scandinavian",
    "AY": "Finnair",
    "EI": "Aer Lingus",
    "U2": "easyJet",
    "FR": "Ryanair",
    "VY": "Vueling",
    "A3": "Aegean Airlines",
    "SN": "Brussels Airlines",
    "LO": "LOT Polish",
    "OK": "Czech Airlines",
    "TK": "Turkish Airlines",
    # Ásia e Oceania
    "EK": "Emirates",
    "QR": "Qatar Airways",
    "EY": "Etihad Airways",
    "SQ": "Singapore Airlines",
    "CX": "Cathay Pacific",
    "JL": "Japan Airlines",
    "NH": "ANA",
    "KE": "Korean Air",
    "OZ": "Asiana Airlines",
    "CI": "China Airlines",
    "BR": "EVA Air",
    "TG": "Thai Airways",
    "MH": "Malaysia Airlines",
    "GA": "Garuda Indonesia",
    "QF": "Qantas",
    "NZ": "Air New Zealand",
    "AI": "Air India",
    "CA": "Air China",
    "MU": "China Eastern",
    "CZ": "China Southern",
    # África
    "ET": "Ethiopian Airlines",
    "SA": "South African Airways",
    "MS": "EgyptAir",
    "AT": "Royal Air Maroc",
}

# Tabela de aeroportos
AIRPORTS = {
    # Brasil
    "GRU": {"cidade": "São Paulo", "nome": "Guarulhos", "pais": "Brasil"},
    "CGH": {"cidade": "São Paulo", "nome": "Congonhas", "pais": "Brasil"},
    "GIG": {"cidade": "Rio de Janeiro", "nome": "Galeão", "pais": "Brasil"},
    "SDU": {"cidade": "Rio de Janeiro", "nome": "Santos Dumont", "pais": "Brasil"},
    "BSB": {"cidade": "Brasília", "nome": "Presidente JK", "pais": "Brasil"},
    "CNF": {"cidade": "Belo Horizonte", "nome": "Confins", "pais": "Brasil"},
    "SSA": {"cidade": "Salvador", "nome": "Deputado Luís Eduardo Magalhães", "pais": "Brasil"},
    "REC": {"cidade": "Recife", "nome": "Guararapes", "pais": "Brasil"},
    "FOR": {"cidade": "Fortaleza", "nome": "Pinto Martins", "pais": "Brasil"},
    "POA": {"cidade": "Porto Alegre", "nome": "Salgado Filho", "pais": "Brasil"},
    "CWB": {"cidade": "Curitiba", "nome": "Afonso Pena", "pais": "Brasil"},
    "FLN": {"cidade": "Florianópolis", "nome": "Hercílio Luz", "pais": "Brasil"},
    "VCP": {"cidade": "Campinas", "nome": "Viracopos", "pais": "Brasil"},
    "NAT": {"cidade": "Natal", "nome": "São Gonçalo do Amarante", "pais": "Brasil"},
    "MCZ": {"cidade": "Maceió", "nome": "Zumbi dos Palmares", "pais": "Brasil"},
    "MAO": {"cidade": "Manaus", "nome": "Eduardo Gomes", "pais": "Brasil"},
    "BEL": {"cidade": "Belém", "nome": "Val de Cans", "pais": "Brasil"},
    
    # América do Sul
    "EZE": {"cidade": "Buenos Aires", "nome": "Ezeiza", "pais": "Argentina"},
    "AEP": {"cidade": "Buenos Aires", "nome": "Aeroparque", "pais": "Argentina"},
    "SCL": {"cidade": "Santiago", "nome": "Arturo Merino Benítez", "pais": "Chile"},
    "LIM": {"cidade": "Lima", "nome": "Jorge Chávez", "pais": "Peru"},
    "BOG": {"cidade": "Bogotá", "nome": "El Dorado", "pais": "Colômbia"},
    "MDE": {"cidade": "Medellín", "nome": "José María Córdova", "pais": "Colômbia"},
    "CTG": {"cidade": "Cartagena", "nome": "Rafael Núñez", "pais": "Colômbia"},
    "UIO": {"cidade": "Quito", "nome": "Mariscal Sucre", "pais": "Equador"},
    "GYE": {"cidade": "Guayaquil", "nome": "José Joaquín de Olmedo", "pais": "Equador"},
    "MVD": {"cidade": "Montevidéu", "nome": "Carrasco", "pais": "Uruguai"},
    "ASU": {"cidade": "Assunção", "nome": "Silvio Pettirossi", "pais": "Paraguai"},
    "VVI": {"cidade": "Santa Cruz", "nome": "Viru Viru", "pais": "Bolívia"},
    "CCS": {"cidade": "Caracas", "nome": "Simón Bolívar", "pais": "Venezuela"},
    
    # América do Norte
    "JFK": {"cidade": "Nova York", "nome": "John F. Kennedy", "pais": "EUA"},
    "EWR": {"cidade": "Nova York", "nome": "Newark", "pais": "EUA"},
    "LGA": {"cidade": "Nova York", "nome": "LaGuardia", "pais": "EUA"},
    "MIA": {"cidade": "Miami", "nome": "Miami International", "pais": "EUA"},
    "FLL": {"cidade": "Fort Lauderdale", "nome": "Fort Lauderdale-Hollywood", "pais": "EUA"},
    "LAX": {"cidade": "Los Angeles", "nome": "Los Angeles International", "pais": "EUA"},
    "SFO": {"cidade": "São Francisco", "nome": "San Francisco International", "pais": "EUA"},
    "ORD": {"cidade": "Chicago", "nome": "O'Hare", "pais": "EUA"},
    "DFW": {"cidade": "Dallas", "nome": "Dallas/Fort Worth", "pais": "EUA"},
    "ATL": {"cidade": "Atlanta", "nome": "Hartsfield-Jackson", "pais": "EUA"},
    "BOS": {"cidade": "Boston", "nome": "Logan", "pais": "EUA"},
    "IAD": {"cidade": "Washington", "nome": "Dulles", "pais": "EUA"},
    "DCA": {"cidade": "Washington", "nome": "Reagan", "pais": "EUA"},
    "SEA": {"cidade": "Seattle", "nome": "Seattle-Tacoma", "pais": "EUA"},
    "LAS": {"cidade": "Las Vegas", "nome": "Harry Reid", "pais": "EUA"},
    "PHX": {"cidade": "Phoenix", "nome": "Sky Harbor", "pais": "EUA"},
    "DEN": {"cidade": "Denver", "nome": "Denver International", "pais": "EUA"},
    "IAH": {"cidade": "Houston", "nome": "George Bush", "pais": "EUA"},
    "MCO": {"cidade": "Orlando", "nome": "Orlando International", "pais": "EUA"},
    "TPA": {"cidade": "Tampa", "nome": "Tampa International", "pais": "EUA"},
    "YYZ": {"cidade": "Toronto", "nome": "Pearson", "pais": "Canadá"},
    "YUL": {"cidade": "Montreal", "nome": "Trudeau", "pais": "Canadá"},
    "YVR": {"cidade": "Vancouver", "nome": "Vancouver International", "pais": "Canadá"},
    "MEX": {"cidade": "Cidade do México", "nome": "Benito Juárez", "pais": "México"},
    "CUN": {"cidade": "Cancún", "nome": "Cancún International", "pais": "México"},
    "GDL": {"cidade": "Guadalajara", "nome": "Miguel Hidalgo", "pais": "México"},
    "PTY": {"cidade": "Cidade do Panamá", "nome": "Tocumen", "pais": "Panamá"},
    "SJO": {"cidade": "San José", "nome": "Juan Santamaría", "pais": "Costa Rica"},
    "HAV": {"cidade": "Havana", "nome": "José Martí", "pais": "Cuba"},
    "SJU": {"cidade": "San Juan", "nome": "Luis Muñoz Marín", "pais": "Porto Rico"},
    
    # Europa
    "LHR": {"cidade": "Londres", "nome": "Heathrow", "pais": "Reino Unido"},
    "LGW": {"cidade": "Londres", "nome": "Gatwick", "pais": "Reino Unido"},
    "STN": {"cidade": "Londres", "nome": "Stansted", "pais": "Reino Unido"},
    "CDG": {"cidade": "Paris", "nome": "Charles de Gaulle", "pais": "França"},
    "ORY": {"cidade": "Paris", "nome": "Orly", "pais": "França"},
    "FRA": {"cidade": "Frankfurt", "nome": "Frankfurt", "pais": "Alemanha"},
    "MUC": {"cidade": "Munique", "nome": "Franz Josef Strauss", "pais": "Alemanha"},
    "AMS": {"cidade": "Amsterdã", "nome": "Schiphol", "pais": "Holanda"},
    "MAD": {"cidade": "Madri", "nome": "Barajas", "pais": "Espanha"},
    "BCN": {"cidade": "Barcelona", "nome": "El Prat", "pais": "Espanha"},
    "FCO": {"cidade": "Roma", "nome": "Fiumicino", "pais": "Itália"},
    "MXP": {"cidade": "Milão", "nome": "Malpensa", "pais": "Itália"},
    "LIS": {"cidade": "Lisboa", "nome": "Humberto Delgado", "pais": "Portugal"},
    "OPO": {"cidade": "Porto", "nome": "Francisco Sá Carneiro", "pais": "Portugal"},
    "ZRH": {"cidade": "Zurique", "nome": "Zurich", "pais": "Suíça"},
    "GVA": {"cidade": "Genebra", "nome": "Geneva", "pais": "Suíça"},
    "VIE": {"cidade": "Viena", "nome": "Vienna", "pais": "Áustria"},
    "BRU": {"cidade": "Bruxelas", "nome": "Brussels", "pais": "Bélgica"},
    "DUB": {"cidade": "Dublin", "nome": "Dublin", "pais": "Irlanda"},
    "CPH": {"cidade": "Copenhague", "nome": "Kastrup", "pais": "Dinamarca"},
    "ARN": {"cidade": "Estocolmo", "nome": "Arlanda", "pais": "Suécia"},
    "OSL": {"cidade": "Oslo", "nome": "Gardermoen", "pais": "Noruega"},
    "HEL": {"cidade": "Helsinque", "nome": "Vantaa", "pais": "Finlândia"},
    "ATH": {"cidade": "Atenas", "nome": "Eleftherios Venizelos", "pais": "Grécia"},
    "IST": {"cidade": "Istambul", "nome": "Istanbul", "pais": "Turquia"},
    "WAW": {"cidade": "Varsóvia", "nome": "Chopin", "pais": "Polônia"},
    "PRG": {"cidade": "Praga", "nome": "Václav Havel", "pais": "República Tcheca"},
    "BUD": {"cidade": "Budapeste", "nome": "Ferenc Liszt", "pais": "Hungria"},
    
    # Ásia
    "DXB": {"cidade": "Dubai", "nome": "Dubai International", "pais": "Emirados Árabes"},
    "AUH": {"cidade": "Abu Dhabi", "nome": "Zayed International", "pais": "Emirados Árabes"},
    "DOH": {"cidade": "Doha", "nome": "Hamad International", "pais": "Catar"},
    "SIN": {"cidade": "Singapura", "nome": "Changi", "pais": "Singapura"},
    "HKG": {"cidade": "Hong Kong", "nome": "Hong Kong International", "pais": "Hong Kong"},
    "NRT": {"cidade": "Tóquio", "nome": "Narita", "pais": "Japão"},
    "HND": {"cidade": "Tóquio", "nome": "Haneda", "pais": "Japão"},
    "ICN": {"cidade": "Seul", "nome": "Incheon", "pais": "Coreia do Sul"},
    "BKK": {"cidade": "Bangkok", "nome": "Suvarnabhumi", "pais": "Tailândia"},
    "KUL": {"cidade": "Kuala Lumpur", "nome": "KLIA", "pais": "Malásia"},
    "CGK": {"cidade": "Jacarta", "nome": "Soekarno-Hatta", "pais": "Indonésia"},
    "DEL": {"cidade": "Nova Delhi", "nome": "Indira Gandhi", "pais": "Índia"},
    "BOM": {"cidade": "Mumbai", "nome": "Chhatrapati Shivaji", "pais": "Índia"},
    "PEK": {"cidade": "Pequim", "nome": "Capital International", "pais": "China"},
    "PVG": {"cidade": "Xangai", "nome": "Pudong", "pais": "China"},
    "TPE": {"cidade": "Taipei", "nome": "Taoyuan", "pais": "Taiwan"},
    "MNL": {"cidade": "Manila", "nome": "Ninoy Aquino", "pais": "Filipinas"},
    "TLV": {"cidade": "Tel Aviv", "nome": "Ben Gurion", "pais": "Israel"},
    
    # Oceania
    "SYD": {"cidade": "Sydney", "nome": "Kingsford Smith", "pais": "Austrália"},
    "MEL": {"cidade": "Melbourne", "nome": "Tullamarine", "pais": "Austrália"},
    "BNE": {"cidade": "Brisbane", "nome": "Brisbane", "pais": "Austrália"},
    "AKL": {"cidade": "Auckland", "nome": "Auckland", "pais": "Nova Zelândia"},
    
    # África
    "JNB": {"cidade": "Joanesburgo", "nome": "O.R. Tambo", "pais": "África do Sul"},
    "CPT": {"cidade": "Cidade do Cabo", "nome": "Cape Town", "pais": "África do Sul"},
    "CAI": {"cidade": "Cairo", "nome": "Cairo International", "pais": "Egito"},
    "CMN": {"cidade": "Casablanca", "nome": "Mohammed V", "pais": "Marrocos"},
    "ADD": {"cidade": "Adis Abeba", "nome": "Bole", "pais": "Etiópia"},
    "NBO": {"cidade": "Nairóbi", "nome": "Jomo Kenyatta", "pais": "Quênia"},
    "LOS": {"cidade": "Lagos", "nome": "Murtala Muhammed", "pais": "Nigéria"},
}

# Função para buscar aeroportos
def search_airports(query):
    query = query.lower().strip()
    results = []
    for code, info in AIRPORTS.items():
        if (query in code.lower() or 
            query in info["cidade"].lower() or 
            query in info["nome"].lower() or
            query in info["pais"].lower()):
            results.append({
                "codigo": code,
                "cidade": info["cidade"],
                "nome": info["nome"],
                "pais": info["pais"]
            })
    return results[:10]  # Limita a 10 resultados

# Função para obter nome da companhia
def get_airline_name(code):
    return AIRLINES.get(code, code)

# Função para carregar dados da planilha
@st.cache_data(ttl=30)
def load_flight_data():
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Detecta número de colunas e ajusta
        expected_columns = ['Data Busca', 'Origem', 'Destino', 'Data Voo', 'Companhia', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas']
        
        if len(df.columns) == 11:
            df.columns = expected_columns
        elif len(df.columns) == 10:
            # Falta uma coluna - provavelmente Paradas
            df.columns = expected_columns[:10]
            df['Paradas'] = 0
        elif len(df.columns) == 8:
            # Versão antiga sem Partida, Chegada, Paradas
            df.columns = expected_columns[:8]
            df['Partida'] = ''
            df['Chegada'] = ''
            df['Paradas'] = 0
        else:
            # Usa as colunas que vieram
            st.warning(f"Planilha com {len(df.columns)} colunas. Esperado: 11")
            return None
        
        df['Preço BRL'] = pd.to_numeric(df['Preço BRL'], errors='coerce')
        df['Paradas'] = pd.to_numeric(df['Paradas'], errors='coerce').fillna(0).astype(int)
        df['Companhia Nome'] = df['Companhia'].apply(get_airline_name)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Função para converter duração ISO para minutos
def duration_to_minutes(duration_str):
    try:
        duration_str = str(duration_str).replace('PT', '')
        hours = 0
        minutes = 0
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0])
            duration_str = duration_str.split('H')[1]
        if 'M' in duration_str:
            minutes = int(duration_str.replace('M', ''))
        return hours * 60 + minutes
    except:
        return 9999

# Função para formatar duração
def format_duration(duration_str):
    try:
        duration_str = str(duration_str).replace('PT', '')
        return duration_str.replace('H', 'h ').replace('M', 'min')
    except:
        return duration_str

# Função para formatar horário
def format_time(datetime_str):
    try:
        if pd.isna(datetime_str) or datetime_str == '':
            return '-'
        # Formato: 2026-01-18T22:50:00
        time_part = str(datetime_str).split('T')[1][:5]
        return time_part
    except:
        return str(datetime_str)

# Função para formatar paradas
def format_stops(stops):
    try:
        stops = int(stops)
        if stops == 0:
            return "Direto"
        elif stops == 1:
            return "1 parada"
        else:
            return f"{stops} paradas"
    except:
        return str(stops)

# Header
st.title("✈️ AirPoint - Busca de Voos")
st.markdown("Pesquise passagens aéreas e compare preços em tempo real.")

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Nova Busca", "📊 Resultados", "🛫 Aeroportos"])

with tab1:
    st.subheader("Buscar Voos")
    
    # Busca de aeroportos
    col1, col2 = st.columns(2)
    
    with col1:
        busca_origem = st.text_input("🔎 Buscar cidade/aeroporto de origem", placeholder="Ex: São Paulo, Miami, Lisboa...")
        if busca_origem:
            resultados_origem = search_airports(busca_origem)
            if resultados_origem:
                opcoes_origem = [f"{r['codigo']} - {r['cidade']} ({r['nome']}, {r['pais']})" for r in resultados_origem]
                selecao_origem = st.selectbox("Selecione o aeroporto de origem:", opcoes_origem, key="sel_origem")
                origem = selecao_origem.split(" - ")[0] if selecao_origem else ""
            else:
                st.warning("Nenhum aeroporto encontrado")
                origem = ""
        else:
            origem = st.text_input("Ou digite o código IATA de origem:", value="GRU", max_chars=3).upper()
    
    with col2:
        busca_destino = st.text_input("🔎 Buscar cidade/aeroporto de destino", placeholder="Ex: Nova York, Paris, Tokyo...")
        if busca_destino:
            resultados_destino = search_airports(busca_destino)
            if resultados_destino:
                opcoes_destino = [f"{r['codigo']} - {r['cidade']} ({r['nome']}, {r['pais']})" for r in resultados_destino]
                selecao_destino = st.selectbox("Selecione o aeroporto de destino:", opcoes_destino, key="sel_destino")
                destino = selecao_destino.split(" - ")[0] if selecao_destino else ""
            else:
                st.warning("Nenhum aeroporto encontrado")
                destino = ""
        else:
            destino = st.text_input("Ou digite o código IATA de destino:", value="MIA", max_chars=3).upper()

    # Data
    data_minima = date.today() + timedelta(days=1)
    data_voo = st.date_input(
        "📅 Data do Voo",
        value=data_minima + timedelta(days=30),
        min_value=data_minima,
        help="Selecione a data de partida"
    )

    st.divider()

    # Botão de busca
    if st.button("🔍 Buscar Voos", type="primary", use_container_width=True):
        
        # Validações
        if len(origem) != 3:
            st.error("❌ Selecione ou digite um código de origem válido (3 letras)")
        elif len(destino) != 3:
            st.error("❌ Selecione ou digite um código de destino válido (3 letras)")
        elif origem == destino:
            st.error("❌ Origem e destino não podem ser iguais")
        else:
            with st.spinner("Buscando voos no Amadeus..."):
                try:
                    params = {
                        "origin": origem,
                        "destination": destino,
                        "date": data_voo.strftime("%Y-%m-%d")
                    }
                    
                    response = requests.get(WEBHOOK_URL, params=params, timeout=60)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Busca realizada! Rota: {origem} → {destino} em {data_voo.strftime('%d/%m/%Y')}")
                        
                        with st.spinner("Processando resultados..."):
                            time.sleep(5)
                        
                        st.cache_data.clear()
                        st.info("👆 Clique na aba **Resultados** para ver os voos encontrados.")
                    else:
                        st.error(f"❌ Erro na busca (código {response.status_code})")
                        
                except requests.exceptions.Timeout:
                    st.warning("⏱️ Busca em andamento. Aguarde alguns segundos e veja a aba Resultados.")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {str(e)}")

with tab2:
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
    
    df = load_flight_data()
    
    if df is not None and len(df) > 0:
        st.subheader("Filtros")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            origens = ['Todas'] + sorted(df['Origem'].unique().tolist())
            filtro_origem = st.selectbox("Origem", origens)
        
        with col2:
            destinos = ['Todos'] + sorted(df['Destino'].unique().tolist())
            filtro_destino = st.selectbox("Destino", destinos)
        
        with col3:
            classes = ['Todas'] + sorted(df['Classe'].unique().tolist())
            filtro_classe = st.selectbox("Classe", classes)
        
        with col4:
            paradas_opcoes = ['Todas', 'Direto', '1 parada', '2+ paradas']
            filtro_paradas = st.selectbox("Paradas", paradas_opcoes)
        
        # Aplica filtros
        df_filtrado = df.copy()
        if filtro_origem != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Origem'] == filtro_origem]
        if filtro_destino != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Destino'] == filtro_destino]
        if filtro_classe != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Classe'] == filtro_classe]
        if filtro_paradas == 'Direto':
            df_filtrado = df_filtrado[df_filtrado['Paradas'] == 0]
        elif filtro_paradas == '1 parada':
            df_filtrado = df_filtrado[df_filtrado['Paradas'] == 1]
        elif filtro_paradas == '2+ paradas':
            df_filtrado = df_filtrado[df_filtrado['Paradas'] >= 2]
        
        st.divider()
        
        if len(df_filtrado) > 0:
            st.subheader("🏆 Melhores Opções")
            
            classes_disponiveis = df_filtrado['Classe'].unique()
            
            for classe in classes_disponiveis:
                df_classe = df_filtrado[df_filtrado['Classe'] == classe].copy()
                
                if len(df_classe) > 0:
                    mais_barato = df_classe.loc[df_classe['Preço BRL'].idxmin()]
                    
                    df_classe['Duracao_Min'] = df_classe['Duração'].apply(duration_to_minutes)
                    mais_rapido = df_classe.loc[df_classe['Duracao_Min'].idxmin()]
                    
                    st.markdown(f"### {classe}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label=f"💰 Mais Barato",
                            value=f"R$ {mais_barato['Preço BRL']:,.2f}",
                        )
                        st.caption(
                            f"**{mais_barato['Companhia Nome']}** ({mais_barato['Companhia']}) | "
                            f"{format_duration(mais_barato['Duração'])} | "
                            f"{format_stops(mais_barato['Paradas'])} | "
                            f"Partida: {format_time(mais_barato['Partida'])}"
                        )
                    
                    with col2:
                        st.metric(
                            label=f"⚡ Mais Rápido",
                            value=format_duration(mais_rapido['Duração']),
                        )
                        st.caption(
                            f"**{mais_rapido['Companhia Nome']}** ({mais_rapido['Companhia']}) | "
                            f"R$ {mais_rapido['Preço BRL']:,.2f} | "
                            f"{format_stops(mais_rapido['Paradas'])} | "
                            f"Partida: {format_time(mais_rapido['Partida'])}"
                        )
                    
                    st.divider()
            
            st.subheader("📋 Todos os Voos")
            
            df_display = df_filtrado[['Origem', 'Destino', 'Data Voo', 'Companhia Nome', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas']].copy()
            df_display.columns = ['Origem', 'Destino', 'Data', 'Companhia', 'Classe', 'Preço', 'Duração', 'Partida', 'Chegada', 'Paradas']
            df_display['Preço'] = df_display['Preço'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['Duração'] = df_display['Duração'].apply(format_duration)
            df_display['Partida'] = df_display['Partida'].apply(format_time)
            df_display['Chegada'] = df_display['Chegada'].apply(format_time)
            df_display['Paradas'] = df_display['Paradas'].apply(format_stops)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Total: {len(df_filtrado)} voos encontrados")
        else:
            st.warning("Nenhum voo encontrado com os filtros selecionados.")
    else:
        st.info("Nenhum dado disponível. Faça uma busca na aba 'Nova Busca'.")

with tab3:
    st.subheader("🛫 Consulta de Aeroportos")
    
    busca_aeroporto = st.text_input("Digite o nome da cidade, país ou código IATA:", placeholder="Ex: Paris, Brasil, JFK...")
    
    if busca_aeroporto:
        resultados = search_airports(busca_aeroporto)
        if resultados:
            df_aeroportos = pd.DataFrame(resultados)
            df_aeroportos.columns = ['Código IATA', 'Cidade', 'Aeroporto', 'País']
            st.dataframe(df_aeroportos, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum aeroporto encontrado para essa busca.")
    else:
        st.info("Digite uma cidade, país ou código para buscar aeroportos.")
    
    st.divider()
    
    with st.expander("📋 Ver todos os aeroportos cadastrados"):
        todos_aeroportos = []
        for code, info in sorted(AIRPORTS.items(), key=lambda x: x[1]['pais']):
            todos_aeroportos.append({
                "Código": code,
                "Cidade": info["cidade"],
                "Aeroporto": info["nome"],
                "País": info["pais"]
            })
        st.dataframe(pd.DataFrame(todos_aeroportos), use_container_width=True, hide_index=True)

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "AirPoint © 2025 - Democratizando viagens com pontos e milhas"
    "</div>",
    unsafe_allow_html=True
)
