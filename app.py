import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta, datetime
import time
import re
import json

# Configuração da página
st.set_page_config(
    page_title="AirPoint - Comparador de Voos",
    page_icon="✈️",
    layout="wide"
)

# URLs
WEBHOOK_URL = "https://hook.us2.make.com/tofuuriqeniuljwnep5jqctntrtttq6r"
SHEET_ID = "1AYmrD_1zwp4D64rs32zMVYhCjn0c4Ubn9RpeUKfK85o"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# Webhook para salvar dados de milhas (você vai criar no Make)
WEBHOOK_MILHAS_URL = "https://hook.us2.make.com/o01sj3mie8xc1ro683sfcayliipnuf8b"

# ============================================
# TABELAS DE DADOS
# ============================================

# Tabela de companhias aéreas
AIRLINES = {
    "LA": "LATAM Airlines", "JJ": "LATAM Brasil", "G3": "Gol", "AD": "Azul",
    "AV": "Avianca", "AR": "Aerolíneas Argentinas", "CM": "Copa Airlines",
    "AA": "American Airlines", "UA": "United Airlines", "DL": "Delta Air Lines",
    "B6": "JetBlue", "AS": "Alaska Airlines", "AC": "Air Canada", "AM": "Aeroméxico",
    "LH": "Lufthansa", "AF": "Air France", "BA": "British Airways", "IB": "Iberia",
    "KL": "KLM", "TP": "TAP Portugal", "LX": "Swiss", "OS": "Austrian Airlines",
    "AY": "Finnair", "TK": "Turkish Airlines", "EK": "Emirates", "QR": "Qatar Airways",
    "EY": "Etihad Airways", "SQ": "Singapore Airlines", "CX": "Cathay Pacific",
    "JL": "Japan Airlines", "NH": "ANA", "QF": "Qantas", "NZ": "Air New Zealand",
    "ET": "Ethiopian Airlines", "SA": "South African Airways",
}

# Tabela de aeroportos
AIRPORTS = {
    # Brasil
    "GRU": {"cidade": "São Paulo", "nome": "Guarulhos", "pais": "Brasil", "regiao": "SAM"},
    "CGH": {"cidade": "São Paulo", "nome": "Congonhas", "pais": "Brasil", "regiao": "SAM"},
    "GIG": {"cidade": "Rio de Janeiro", "nome": "Galeão", "pais": "Brasil", "regiao": "SAM"},
    "BSB": {"cidade": "Brasília", "nome": "Presidente JK", "pais": "Brasil", "regiao": "SAM"},
    "CNF": {"cidade": "Belo Horizonte", "nome": "Confins", "pais": "Brasil", "regiao": "SAM"},
    "SSA": {"cidade": "Salvador", "nome": "Deputado Luís Eduardo Magalhães", "pais": "Brasil", "regiao": "SAM"},
    "REC": {"cidade": "Recife", "nome": "Guararapes", "pais": "Brasil", "regiao": "SAM"},
    "FOR": {"cidade": "Fortaleza", "nome": "Pinto Martins", "pais": "Brasil", "regiao": "SAM"},
    "POA": {"cidade": "Porto Alegre", "nome": "Salgado Filho", "pais": "Brasil", "regiao": "SAM"},
    "CWB": {"cidade": "Curitiba", "nome": "Afonso Pena", "pais": "Brasil", "regiao": "SAM"},
    "FLN": {"cidade": "Florianópolis", "nome": "Hercílio Luz", "pais": "Brasil", "regiao": "SAM"},
    "VCP": {"cidade": "Campinas", "nome": "Viracopos", "pais": "Brasil", "regiao": "SAM"},
    "NAT": {"cidade": "Natal", "nome": "São Gonçalo do Amarante", "pais": "Brasil", "regiao": "SAM"},
    "MAO": {"cidade": "Manaus", "nome": "Eduardo Gomes", "pais": "Brasil", "regiao": "SAM"},
    # América do Sul
    "EZE": {"cidade": "Buenos Aires", "nome": "Ezeiza", "pais": "Argentina", "regiao": "SAM"},
    "SCL": {"cidade": "Santiago", "nome": "Arturo Merino Benítez", "pais": "Chile", "regiao": "SAM"},
    "LIM": {"cidade": "Lima", "nome": "Jorge Chávez", "pais": "Peru", "regiao": "SAM"},
    "BOG": {"cidade": "Bogotá", "nome": "El Dorado", "pais": "Colômbia", "regiao": "SAM"},
    "MVD": {"cidade": "Montevidéu", "nome": "Carrasco", "pais": "Uruguai", "regiao": "SAM"},
    # América do Norte
    "JFK": {"cidade": "Nova York", "nome": "John F. Kennedy", "pais": "EUA", "regiao": "NAM"},
    "EWR": {"cidade": "Nova York", "nome": "Newark", "pais": "EUA", "regiao": "NAM"},
    "MIA": {"cidade": "Miami", "nome": "Miami International", "pais": "EUA", "regiao": "NAM"},
    "LAX": {"cidade": "Los Angeles", "nome": "Los Angeles International", "pais": "EUA", "regiao": "NAM"},
    "SFO": {"cidade": "São Francisco", "nome": "San Francisco International", "pais": "EUA", "regiao": "NAM"},
    "ORD": {"cidade": "Chicago", "nome": "O'Hare", "pais": "EUA", "regiao": "NAM"},
    "DFW": {"cidade": "Dallas", "nome": "Dallas/Fort Worth", "pais": "EUA", "regiao": "NAM"},
    "ATL": {"cidade": "Atlanta", "nome": "Hartsfield-Jackson", "pais": "EUA", "regiao": "NAM"},
    "MCO": {"cidade": "Orlando", "nome": "Orlando International", "pais": "EUA", "regiao": "NAM"},
    "YYZ": {"cidade": "Toronto", "nome": "Pearson", "pais": "Canadá", "regiao": "NAM"},
    "MEX": {"cidade": "Cidade do México", "nome": "Benito Juárez", "pais": "México", "regiao": "NAM"},
    "CUN": {"cidade": "Cancún", "nome": "Cancún International", "pais": "México", "regiao": "NAM"},
    "PTY": {"cidade": "Cidade do Panamá", "nome": "Tocumen", "pais": "Panamá", "regiao": "NAM"},
    # Europa
    "LHR": {"cidade": "Londres", "nome": "Heathrow", "pais": "Reino Unido", "regiao": "EUR"},
    "CDG": {"cidade": "Paris", "nome": "Charles de Gaulle", "pais": "França", "regiao": "EUR"},
    "FRA": {"cidade": "Frankfurt", "nome": "Frankfurt", "pais": "Alemanha", "regiao": "EUR"},
    "AMS": {"cidade": "Amsterdã", "nome": "Schiphol", "pais": "Holanda", "regiao": "EUR"},
    "MAD": {"cidade": "Madri", "nome": "Barajas", "pais": "Espanha", "regiao": "EUR"},
    "BCN": {"cidade": "Barcelona", "nome": "El Prat", "pais": "Espanha", "regiao": "EUR"},
    "FCO": {"cidade": "Roma", "nome": "Fiumicino", "pais": "Itália", "regiao": "EUR"},
    "MXP": {"cidade": "Milão", "nome": "Malpensa", "pais": "Itália", "regiao": "EUR"},
    "LIS": {"cidade": "Lisboa", "nome": "Humberto Delgado", "pais": "Portugal", "regiao": "EUR"},
    "OPO": {"cidade": "Porto", "nome": "Francisco Sá Carneiro", "pais": "Portugal", "regiao": "EUR"},
    "ZRH": {"cidade": "Zurique", "nome": "Zurich", "pais": "Suíça", "regiao": "EUR"},
    "IST": {"cidade": "Istambul", "nome": "Istanbul", "pais": "Turquia", "regiao": "EUR"},
    # Oriente Médio
    "DXB": {"cidade": "Dubai", "nome": "Dubai International", "pais": "Emirados Árabes", "regiao": "MDE"},
    "DOH": {"cidade": "Doha", "nome": "Hamad International", "pais": "Catar", "regiao": "MDE"},
    "AUH": {"cidade": "Abu Dhabi", "nome": "Zayed International", "pais": "Emirados Árabes", "regiao": "MDE"},
    "TLV": {"cidade": "Tel Aviv", "nome": "Ben Gurion", "pais": "Israel", "regiao": "MDE"},
    # Ásia
    "SIN": {"cidade": "Singapura", "nome": "Changi", "pais": "Singapura", "regiao": "ASIA"},
    "HKG": {"cidade": "Hong Kong", "nome": "Hong Kong International", "pais": "Hong Kong", "regiao": "ASIA"},
    "NRT": {"cidade": "Tóquio", "nome": "Narita", "pais": "Japão", "regiao": "ASIA"},
    "ICN": {"cidade": "Seul", "nome": "Incheon", "pais": "Coreia do Sul", "regiao": "ASIA"},
    "BKK": {"cidade": "Bangkok", "nome": "Suvarnabhumi", "pais": "Tailândia", "regiao": "ASIA"},
    "PEK": {"cidade": "Pequim", "nome": "Capital International", "pais": "China", "regiao": "ASIA"},
    "PVG": {"cidade": "Xangai", "nome": "Pudong", "pais": "China", "regiao": "ASIA"},
    # Oceania
    "SYD": {"cidade": "Sydney", "nome": "Kingsford Smith", "pais": "Austrália", "regiao": "OCE"},
    "AKL": {"cidade": "Auckland", "nome": "Auckland", "pais": "Nova Zelândia", "regiao": "OCE"},
    # África
    "JNB": {"cidade": "Joanesburgo", "nome": "O.R. Tambo", "pais": "África do Sul", "regiao": "AFR"},
    "CPT": {"cidade": "Cidade do Cabo", "nome": "Cape Town", "pais": "África do Sul", "regiao": "AFR"},
    "CAI": {"cidade": "Cairo", "nome": "Cairo International", "pais": "Egito", "regiao": "AFR"},
}

# ============================================
# TABELAS DE MILHAS POR PROGRAMA (AWARD CHARTS)
# ============================================

# Estrutura: origem_regiao -> destino_regiao -> {programa: {economy: X, business: Y, first: Z}}
# Regiões: SAM (América do Sul), NAM (América do Norte), EUR (Europa), MDE (Oriente Médio), ASIA, OCE (Oceania), AFR (África)

AWARD_CHARTS = {
    # América do Sul -> América do Norte
    ("SAM", "NAM"): {
        "AAdvantage": {"economy": 30000, "business": 57500, "first": 85000},
        "Iberia Plus": {"economy": 34000, "business": 68000, "first": 102000},
        "TAP Miles&Go": {"economy": 35000, "business": 70000, "first": 105000},
        "Smiles": {"economy": 45000, "business": 90000, "first": None},  # Dinâmico - referência
        "LATAM Pass": {"economy": 50000, "business": 100000, "first": None},  # Dinâmico - referência
    },
    # América do Sul -> Europa
    ("SAM", "EUR"): {
        "AAdvantage": {"economy": 45000, "business": 75000, "first": 100000},
        "Iberia Plus": {"economy": 34000, "business": 68000, "first": 102000},
        "TAP Miles&Go": {"economy": 40000, "business": 75000, "first": 112500},
        "Smiles": {"economy": 50000, "business": 100000, "first": None},
        "LATAM Pass": {"economy": 55000, "business": 110000, "first": None},
    },
    # América do Sul -> Oriente Médio
    ("SAM", "MDE"): {
        "AAdvantage": {"economy": 50000, "business": 85000, "first": 115000},
        "Iberia Plus": {"economy": 53000, "business": 106000, "first": 159000},
        "Smiles": {"economy": 70000, "business": 140000, "first": None},
        "LATAM Pass": {"economy": 75000, "business": 150000, "first": None},
    },
    # América do Sul -> Ásia
    ("SAM", "ASIA"): {
        "AAdvantage": {"economy": 55000, "business": 100000, "first": 140000},
        "Smiles": {"economy": 80000, "business": 160000, "first": None},
        "LATAM Pass": {"economy": 85000, "business": 170000, "first": None},
    },
    # América do Sul -> Oceania
    ("SAM", "OCE"): {
        "AAdvantage": {"economy": 60000, "business": 110000, "first": 150000},
        "Smiles": {"economy": 90000, "business": 180000, "first": None},
    },
    # América do Sul -> África
    ("SAM", "AFR"): {
        "AAdvantage": {"economy": 50000, "business": 85000, "first": 115000},
        "Smiles": {"economy": 75000, "business": 150000, "first": None},
    },
    # Doméstico América do Sul
    ("SAM", "SAM"): {
        "Smiles": {"economy": 15000, "business": 40000, "first": None},
        "LATAM Pass": {"economy": 18000, "business": 45000, "first": None},
        "Azul Fidelidade": {"economy": 12000, "business": 35000, "first": None},
    },
    # América do Norte -> Europa
    ("NAM", "EUR"): {
        "AAdvantage": {"economy": 45000, "business": 75000, "first": 100000},
        "Iberia Plus": {"economy": 34000, "business": 68000, "first": 102000},
    },
}

# Custos médios de aquisição de milhas (R$ por 1.000 milhas)
CUSTO_AQUISICAO_MILHAS = {
    "Smiles": {
        "compra_direta": 35.0,  # Compra sem promoção
        "compra_promo": 22.0,   # Com promoção ~40% off
        "transferencia_normal": 30.0,  # Livelo/Esfera 1:1
        "transferencia_bonus": 18.0,   # Com bônus 70%+
        "clube_smiles": 20.0,   # Assinatura mensal
    },
    "LATAM Pass": {
        "compra_direta": 38.0,
        "compra_promo": 25.0,
        "transferencia_normal": 32.0,
        "transferencia_bonus": 19.0,
    },
    "AAdvantage": {
        "compra_direta": 45.0,  # Em dólar, convertido
        "transferencia_esfera": 25.0,  # Esfera com bônus
    },
    "Azul Fidelidade": {
        "compra_direta": 32.0,
        "compra_promo": 20.0,
        "clube_azul": 18.0,
    },
    "Iberia Plus": {
        "transferencia_esfera": 22.0,  # Esfera com bônus
        "compra_promo": 28.0,
    },
    "TAP Miles&Go": {
        "transferencia_livelo": 20.0,  # Livelo com bônus
    },
}

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def get_region(airport_code):
    """Retorna a região de um aeroporto"""
    if airport_code in AIRPORTS:
        return AIRPORTS[airport_code].get("regiao", "SAM")
    return "SAM"  # Default

def get_award_prices(origin, destination):
    """Retorna preços em milhas para a rota"""
    origin_region = get_region(origin)
    dest_region = get_region(destination)
    
    # Tenta encontrar a rota direta
    key = (origin_region, dest_region)
    if key in AWARD_CHARTS:
        return AWARD_CHARTS[key]
    
    # Tenta rota inversa
    key_reverse = (dest_region, origin_region)
    if key_reverse in AWARD_CHARTS:
        return AWARD_CHARTS[key_reverse]
    
    return None

def calculate_cpp(cash_price, miles_needed):
    """Calcula centavos por ponto/milha (CPP)"""
    if miles_needed and miles_needed > 0:
        return (cash_price / miles_needed) * 100  # Centavos por milha
    return 0

def calculate_value_per_mile(cash_price, miles_needed):
    """Calcula valor em R$ por 1.000 milhas"""
    if miles_needed and miles_needed > 0:
        return (cash_price / miles_needed) * 1000
    return 0

def is_worth_using_miles(cash_price, miles_needed, acquisition_cost_per_1k):
    """Determina se vale a pena usar milhas"""
    if not miles_needed or miles_needed == 0:
        return None, 0
    
    value_per_1k = calculate_value_per_mile(cash_price, miles_needed)
    savings_percent = ((value_per_1k - acquisition_cost_per_1k) / value_per_1k) * 100 if value_per_1k > 0 else 0
    
    return value_per_1k > acquisition_cost_per_1k, savings_percent

def search_airports(query):
    """Busca aeroportos por cidade, código ou país"""
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
    return results[:10]

def get_airline_name(code):
    """Retorna nome da companhia aérea"""
    return AIRLINES.get(code, code)

@st.cache_data(ttl=30)
def load_flight_data():
    """Carrega dados da planilha"""
    try:
        df = pd.read_csv(SHEET_URL)
        expected_columns = ['Data Busca', 'Origem', 'Destino', 'Data Voo', 'Companhia', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas']
        
        if len(df.columns) == 11:
            df.columns = expected_columns
        elif len(df.columns) == 10:
            df.columns = expected_columns[:10]
            df['Paradas'] = 0
        elif len(df.columns) == 8:
            df.columns = expected_columns[:8]
            df['Partida'] = ''
            df['Chegada'] = ''
            df['Paradas'] = 0
        else:
            st.warning(f"Planilha com {len(df.columns)} colunas. Esperado: 11")
            return None
        
        df['Preço BRL'] = pd.to_numeric(df['Preço BRL'], errors='coerce')
        df['Paradas'] = pd.to_numeric(df['Paradas'], errors='coerce').fillna(0).astype(int)
        df['Companhia Nome'] = df['Companhia'].apply(get_airline_name)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def format_duration(duration_str):
    """Formata duração ISO para legível"""
    try:
        duration_str = str(duration_str).replace('PT', '')
        return duration_str.replace('H', 'h ').replace('M', 'min')
    except:
        return duration_str

def format_time(datetime_str):
    """Formata horário"""
    try:
        if pd.isna(datetime_str) or datetime_str == '':
            return '-'
        time_part = str(datetime_str).split('T')[1][:5]
        return time_part
    except:
        return str(datetime_str)

def format_stops(stops):
    """Formata paradas"""
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

def duration_to_minutes(duration_str):
    """Converte duração para minutos"""
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

# ============================================
# FUNÇÕES PARA PARSING DE RESULTADOS DO SEATS.AERO
# ============================================

def parse_miles_from_text(text):
    """
    Parser inteligente para extrair dados de disponibilidade de milhas
    do texto retornado pelo Seats.aero Assistant
    """
    results = []
    
    # Padrões comuns de milhas (30,000 / 30000 / 30.000 / 30k)
    miles_patterns = [
        r'(\d{1,3}[,.\s]?\d{3})\s*(?:miles|milhas|mi)',
        r'(\d{2,3})k\s*(?:miles|milhas)?',
        r'(\d{1,3}[,.\s]?\d{3})\s*(?:pts|points|pontos)',
    ]
    
    # Padrões de programas
    program_patterns = {
        'Smiles': r'(?i)(smiles|gol)',
        'AAdvantage': r'(?i)(aadvantage|american\s*airlines|aa\b)',
        'United MileagePlus': r'(?i)(mileageplus|united)',
        'Delta SkyMiles': r'(?i)(skymiles|delta)',
        'Azul': r'(?i)(tudoazul|azul)',
        'Aeroplan': r'(?i)(aeroplan|air\s*canada)',
        'Flying Blue': r'(?i)(flying\s*blue|air\s*france|klm)',
        'Emirates Skywards': r'(?i)(skywards|emirates)',
        'Etihad Guest': r'(?i)(etihad)',
        'LATAM Pass': r'(?i)(latam\s*pass|latam)',
        'TAP Miles&Go': r'(?i)(miles\s*&\s*go|tap)',
        'Iberia Plus': r'(?i)(iberia\s*plus|iberia)',
        'Qatar Privilege': r'(?i)(privilege|qatar)',
        'Turkish Miles': r'(?i)(turkish|miles\s*&\s*smiles)',
    }
    
    # Padrões de classe
    class_patterns = {
        'Economy': r'(?i)(economy|econ|Y\b|econômica)',
        'Premium Economy': r'(?i)(premium\s*economy|premium\s*econ|W\b)',
        'Business': r'(?i)(business|executiva|J\b)',
        'First': r'(?i)(first|primeira|F\b)',
    }
    
    # Padrões de data
    date_patterns = [
        r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        r'(\d{1,2}\s+(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-z]*\s*\d{2,4})',
        r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s*\d{2,4})',
    ]
    
    # Padrão de companhias aéreas
    airline_codes = '|'.join(AIRLINES.keys())
    airline_pattern = rf'\b({airline_codes})\b'
    
    # Divide o texto em linhas ou blocos
    lines = text.split('\n')
    
    current_result = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_result and 'milhas' in current_result:
                results.append(current_result)
                current_result = {}
            continue
        
        # Busca milhas
        for pattern in miles_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                miles_str = match.group(1)
                # Limpa e converte
                miles_str = miles_str.replace(',', '').replace('.', '').replace(' ', '')
                if 'k' in line.lower():
                    miles_str = miles_str + '000'
                try:
                    current_result['milhas'] = int(miles_str)
                except:
                    pass
        
        # Busca programa
        for program, pattern in program_patterns.items():
            if re.search(pattern, line):
                current_result['programa'] = program
                break
        
        # Busca classe
        for cabin, pattern in class_patterns.items():
            if re.search(pattern, line):
                current_result['classe'] = cabin
                break
        
        # Busca data
        for pattern in date_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                current_result['data'] = match.group(1)
                break
        
        # Busca companhia
        match = re.search(airline_pattern, line)
        if match:
            current_result['companhia'] = match.group(1)
        
        # Busca se é direto ou conexão
        if re.search(r'(?i)(direto|direct|nonstop|non-stop)', line):
            current_result['paradas'] = 'Direto'
        elif re.search(r'(?i)(1\s*(?:stop|parada|conexão)|one\s*stop)', line):
            current_result['paradas'] = '1 parada'
        elif re.search(r'(?i)(2\s*(?:stops|paradas|conexões)|two\s*stops)', line):
            current_result['paradas'] = '2 paradas'
        
        # Busca assentos disponíveis
        seats_match = re.search(r'(\d+)\s*(?:seats?|assentos?|vagas?)', line, re.IGNORECASE)
        if seats_match:
            current_result['assentos'] = int(seats_match.group(1))
    
    # Adiciona último resultado se existir
    if current_result and 'milhas' in current_result:
        results.append(current_result)
    
    return results

def classify_deal_quality(milhas, classe, custo_por_mil, preco_cash=None):
    """
    Classifica a qualidade do deal baseado em benchmarks do mercado
    Retorna: ('excelente', 'bom', 'regular', 'ruim') e o motivo
    """
    # Benchmarks de valor por 1k milhas (R$)
    benchmarks = {
        'Economy': {'excelente': 25, 'bom': 35, 'regular': 50},
        'Premium Economy': {'excelente': 35, 'bom': 50, 'regular': 70},
        'Business': {'excelente': 50, 'bom': 70, 'regular': 100},
        'First': {'excelente': 70, 'bom': 100, 'regular': 150},
    }
    
    bench = benchmarks.get(classe, benchmarks['Economy'])
    
    if preco_cash and milhas > 0:
        valor_por_mil = (preco_cash / milhas) * 1000
        
        if valor_por_mil >= bench['excelente']:
            return 'excelente', f"Valor de R$ {valor_por_mil:.2f}/1k milhas é excelente!"
        elif valor_por_mil >= bench['bom']:
            return 'bom', f"Valor de R$ {valor_por_mil:.2f}/1k milhas é bom"
        elif valor_por_mil >= bench['regular']:
            return 'regular', f"Valor de R$ {valor_por_mil:.2f}/1k milhas é regular"
        else:
            return 'ruim', f"Valor de R$ {valor_por_mil:.2f}/1k milhas é baixo"
    
    return 'indefinido', "Não foi possível avaliar"

def check_alerts(results, custo_por_mil=20.0, preco_cash=None):
    """
    Verifica se algum resultado merece um alerta de oportunidade
    """
    alerts = []
    
    for result in results:
        milhas = result.get('milhas', 0)
        classe = result.get('classe', 'Economy')
        programa = result.get('programa', 'Desconhecido')
        
        if milhas > 0:
            custo_total = (milhas / 1000) * custo_por_mil
            
            # Benchmarks de "bom negócio" por classe
            thresholds = {
                'Economy': 1500,      # Se custar menos que R$ 1.500 em milhas
                'Premium Economy': 3000,
                'Business': 5000,
                'First': 8000,
            }
            
            threshold = thresholds.get(classe, 2000)
            
            if custo_total < threshold:
                quality, reason = classify_deal_quality(milhas, classe, custo_por_mil, preco_cash)
                
                if quality in ['excelente', 'bom']:
                    alerts.append({
                        'tipo': 'oportunidade',
                        'qualidade': quality,
                        'programa': programa,
                        'classe': classe,
                        'milhas': milhas,
                        'custo_estimado': custo_total,
                        'mensagem': f"🎯 {programa}: {milhas:,} milhas em {classe} = R$ {custo_total:,.2f}",
                        'razao': reason
                    })
            
            # Alerta de preço muito baixo (possível erro de tarifa)
            if classe == 'Business' and milhas < 40000:
                alerts.append({
                    'tipo': 'erro_tarifa',
                    'programa': programa,
                    'classe': classe,
                    'milhas': milhas,
                    'mensagem': f"⚠️ POSSÍVEL ERRO: {programa} {classe} por apenas {milhas:,} milhas!"
                })
    
    return alerts

def save_miles_search(origem, destino, data_busca, resultados, webhook_url):
    """
    Salva a busca de milhas via webhook do Make para histórico
    """
    try:
        payload = {
            "data_busca": datetime.now().isoformat(),
            "origem": origem,
            "destino": destino,
            "data_voo": data_busca,
            "resultados": json.dumps(resultados, ensure_ascii=False),
            "quantidade_opcoes": len(resultados)
        }
        
        response = requests.post(webhook_url, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        return False

# Inicializa histórico na sessão
if 'historico_milhas' not in st.session_state:
    st.session_state.historico_milhas = []

if 'alertas_ativos' not in st.session_state:
    st.session_state.alertas_ativos = []

# ============================================
# INTERFACE
# ============================================

st.title("✈️ AirPoint - Comparador de Voos")
st.markdown("Compare preços em dinheiro vs. pontos e milhas")

st.divider()

# Tabs principais
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Nova Busca", "📊 Resultados", "🎫 Buscar Milhas", "🎯 Comparador", "🛫 Aeroportos"])

# ============================================
# TAB 1: NOVA BUSCA
# ============================================
with tab1:
    st.subheader("Buscar Voos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        busca_origem = st.text_input("🔎 Buscar cidade de origem", placeholder="Ex: São Paulo, Miami...")
        if busca_origem:
            resultados_origem = search_airports(busca_origem)
            if resultados_origem:
                opcoes_origem = [f"{r['codigo']} - {r['cidade']} ({r['pais']})" for r in resultados_origem]
                selecao_origem = st.selectbox("Selecione:", opcoes_origem, key="sel_origem")
                origem = selecao_origem.split(" - ")[0]
            else:
                st.warning("Nenhum aeroporto encontrado")
                origem = ""
        else:
            origem = st.text_input("Código IATA origem:", value="GRU", max_chars=3).upper()
    
    with col2:
        busca_destino = st.text_input("🔎 Buscar cidade de destino", placeholder="Ex: Nova York, Paris...")
        if busca_destino:
            resultados_destino = search_airports(busca_destino)
            if resultados_destino:
                opcoes_destino = [f"{r['codigo']} - {r['cidade']} ({r['pais']})" for r in resultados_destino]
                selecao_destino = st.selectbox("Selecione:", opcoes_destino, key="sel_destino")
                destino = selecao_destino.split(" - ")[0]
            else:
                st.warning("Nenhum aeroporto encontrado")
                destino = ""
        else:
            destino = st.text_input("Código IATA destino:", value="MIA", max_chars=3).upper()

    data_minima = date.today() + timedelta(days=1)
    data_voo = st.date_input(
        "📅 Data do Voo",
        value=data_minima + timedelta(days=30),
        min_value=data_minima,
    )

    st.divider()

    if st.button("🔍 Buscar Voos", type="primary", use_container_width=True):
        if len(origem) != 3 or len(destino) != 3 or origem == destino:
            st.error("❌ Verifique os códigos de origem e destino")
        else:
            with st.spinner("Buscando voos..."):
                try:
                    params = {"origin": origem, "destination": destino, "date": data_voo.strftime("%Y-%m-%d")}
                    response = requests.get(WEBHOOK_URL, params=params, timeout=60)
                    
                    if response.status_code == 200:
                        st.success(f"✅ Busca realizada! {origem} → {destino}")
                        with st.spinner("Processando..."):
                            time.sleep(5)
                        st.cache_data.clear()
                        st.info("👆 Veja os resultados nas abas **Resultados** e **Comparador Milhas**")
                    else:
                        st.error(f"❌ Erro (código {response.status_code})")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

# ============================================
# TAB 2: RESULTADOS
# ============================================
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
            
            for classe in df_filtrado['Classe'].unique():
                df_classe = df_filtrado[df_filtrado['Classe'] == classe].copy()
                
                if len(df_classe) > 0:
                    mais_barato = df_classe.loc[df_classe['Preço BRL'].idxmin()]
                    df_classe['Duracao_Min'] = df_classe['Duração'].apply(duration_to_minutes)
                    mais_rapido = df_classe.loc[df_classe['Duracao_Min'].idxmin()]
                    
                    st.markdown(f"### {classe}")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(label="💰 Mais Barato", value=f"R$ {mais_barato['Preço BRL']:,.2f}")
                        st.caption(f"**{mais_barato['Companhia Nome']}** | {format_duration(mais_barato['Duração'])} | {format_stops(mais_barato['Paradas'])}")
                    
                    with col2:
                        st.metric(label="⚡ Mais Rápido", value=format_duration(mais_rapido['Duração']))
                        st.caption(f"**{mais_rapido['Companhia Nome']}** | R$ {mais_rapido['Preço BRL']:,.2f} | {format_stops(mais_rapido['Paradas'])}")
                    
                    st.divider()
            
            st.subheader("📋 Todos os Voos")
            df_display = df_filtrado[['Origem', 'Destino', 'Data Voo', 'Companhia Nome', 'Classe', 'Preço BRL', 'Duração', 'Partida', 'Chegada', 'Paradas']].copy()
            df_display.columns = ['Origem', 'Destino', 'Data', 'Companhia', 'Classe', 'Preço', 'Duração', 'Partida', 'Chegada', 'Paradas']
            df_display['Preço'] = df_display['Preço'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['Duração'] = df_display['Duração'].apply(format_duration)
            df_display['Partida'] = df_display['Partida'].apply(format_time)
            df_display['Chegada'] = df_display['Chegada'].apply(format_time)
            df_display['Paradas'] = df_display['Paradas'].apply(format_stops)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.caption(f"Total: {len(df_filtrado)} voos")
        else:
            st.warning("Nenhum voo encontrado com os filtros.")
    else:
        st.info("Faça uma busca na aba 'Nova Busca'.")

# ============================================
# TAB 3: BUSCAR MILHAS (Semi-automatizado com Parser e Alertas)
# ============================================
with tab3:
    st.subheader("🎫 Buscar Disponibilidade de Milhas")
    st.markdown("Use o **Seats.aero Assistant** para encontrar award seats disponíveis")
    
    # Mostra alertas ativos no topo
    if st.session_state.alertas_ativos:
        with st.expander(f"🔔 Alertas Ativos ({len(st.session_state.alertas_ativos)})", expanded=True):
            for alerta in st.session_state.alertas_ativos[-5:]:  # Últimos 5
                if alerta.get('tipo') == 'erro_tarifa':
                    st.error(alerta['mensagem'])
                elif alerta.get('qualidade') == 'excelente':
                    st.success(alerta['mensagem'])
                else:
                    st.info(alerta['mensagem'])
            
            if st.button("🗑️ Limpar Alertas"):
                st.session_state.alertas_ativos = []
                st.rerun()
    
    st.divider()
    
    # Configuração de custo de aquisição (para alertas)
    with st.expander("⚙️ Configurar custo de aquisição de milhas"):
        custo_usuario_mil = st.number_input(
            "Seu custo médio por 1.000 milhas (R$)",
            value=20.0,
            min_value=0.0,
            step=1.0,
            help="Usado para calcular se uma oferta é boa",
            key="custo_mil_tab3"
        )
    
    st.divider()
    
    # Passo 1: Definir busca
    st.markdown("### 1️⃣ Defina sua busca")
    
    col1, col2 = st.columns(2)
    with col1:
        busca_origem_milhas = st.text_input("Origem (código IATA)", value="GRU", max_chars=3, key="milhas_origem").upper()
    with col2:
        busca_destino_milhas = st.text_input("Destino (código IATA)", value="MIA", max_chars=3, key="milhas_destino").upper()
    
    col3, col4 = st.columns(2)
    with col3:
        data_inicio_milhas = st.date_input(
            "Data inicial",
            value=date.today() + timedelta(days=30),
            min_value=date.today() + timedelta(days=1),
            key="milhas_data_inicio"
        )
    with col4:
        data_fim_milhas = st.date_input(
            "Data final (opcional)",
            value=data_inicio_milhas + timedelta(days=7),
            min_value=data_inicio_milhas,
            key="milhas_data_fim"
        )
    
    col5, col6 = st.columns(2)
    with col5:
        cabines = st.multiselect(
            "Cabines",
            ["Economy", "Premium Economy", "Business", "First"],
            default=["Economy", "Business"],
            key="milhas_cabines"
        )
    with col6:
        programas_preferidos = st.multiselect(
            "Programas preferidos (opcional)",
            ["Smiles", "AAdvantage", "United MileagePlus", "Delta SkyMiles", "Azul", "Air Canada Aeroplan", "Flying Blue", "Emirates", "Etihad"],
            default=[],
            key="milhas_programas"
        )
    
    st.divider()
    
    # Passo 2: Gerar prompt
    st.markdown("### 2️⃣ Copie o prompt para o Seats.aero Assistant")
    
    # Monta cidade de origem/destino se disponível
    origem_nome = AIRPORTS.get(busca_origem_milhas, {}).get("cidade", busca_origem_milhas)
    destino_nome = AIRPORTS.get(busca_destino_milhas, {}).get("cidade", busca_destino_milhas)
    
    # Formata datas
    data_inicio_str = data_inicio_milhas.strftime("%d/%m/%Y")
    data_fim_str = data_fim_milhas.strftime("%d/%m/%Y")
    
    # Monta lista de cabines
    cabines_str = ", ".join(cabines) if cabines else "Economy e Business"
    
    # Monta prompt otimizado
    prompt_base = f"""Busque disponibilidade de passagens award de {busca_origem_milhas} ({origem_nome}) para {busca_destino_milhas} ({destino_nome}).

Período: {data_inicio_str} a {data_fim_str}
Cabines: {cabines_str}
"""
    
    if programas_preferidos:
        prompt_base += f"Programas preferidos: {', '.join(programas_preferidos)}\n"
    
    prompt_base += """
Por favor, liste as opções disponíveis com:
- Programa de milhas
- Data do voo
- Número do voo
- Quantidade de milhas necessárias
- Classe (Economy/Business/First)
- Companhia aérea operadora
- Se é voo direto ou com conexão
- Quantidade de assentos disponíveis (se souber)

Ordene do menor para o maior custo em milhas."""

    st.code(prompt_base, language=None)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.markdown(
            f'<a href="https://seats.aero/assistant" target="_blank">'
            f'<button style="background-color:#FF6B6B;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;width:100%">'
            f'🚀 Abrir Seats.aero Assistant</button></a>',
            unsafe_allow_html=True
        )
    with col_btn2:
        if st.button("📋 Copiar Prompt", use_container_width=True, key="copy_prompt"):
            st.toast("Use Ctrl+C para copiar o texto acima!")
    
    st.divider()
    
    # Passo 3: Colar resultado
    st.markdown("### 3️⃣ Cole o resultado do Assistant")
    st.caption("Após receber a resposta do Seats.aero Assistant, cole aqui:")
    
    resultado_assistant = st.text_area(
        "Resultado do Seats.aero Assistant",
        height=200,
        placeholder="Cole aqui a resposta completa do Seats.aero Assistant...",
        key="resultado_seats"
    )
    
    # Botão para processar
    processar_resultado = st.button("🔍 Processar Resultado", type="primary", use_container_width=True)
    
    # Passo 4: Processar e comparar
    if resultado_assistant and processar_resultado:
        st.divider()
        st.markdown("### 4️⃣ Análise Automática")
        
        # Parser automático
        with st.spinner("Extraindo dados..."):
            resultados_parseados = parse_miles_from_text(resultado_assistant)
        
        # Busca preço cash para comparação
        df = load_flight_data()
        preco_cash_ref = None
        if df is not None and len(df) > 0:
            df_rota = df[(df['Origem'] == busca_origem_milhas) & (df['Destino'] == busca_destino_milhas)]
            if len(df_rota) > 0:
                preco_cash_ref = df_rota['Preço BRL'].min()
        
        if resultados_parseados:
            st.success(f"✅ Encontradas **{len(resultados_parseados)} opções** de milhas!")
            
            # Verifica alertas
            alertas = check_alerts(resultados_parseados, custo_usuario_mil, preco_cash_ref)
            if alertas:
                st.session_state.alertas_ativos.extend(alertas)
                for alerta in alertas:
                    if alerta.get('tipo') == 'erro_tarifa':
                        st.error(f"🚨 {alerta['mensagem']}")
                    elif alerta.get('qualidade') == 'excelente':
                        st.balloons()
                        st.success(f"🎉 OPORTUNIDADE: {alerta['mensagem']}")
                    elif alerta.get('qualidade') == 'bom':
                        st.success(alerta['mensagem'])
            
            st.divider()
            
            # Tabela de resultados parseados
            st.markdown("#### 📊 Opções Encontradas")
            
            # Converte para DataFrame
            df_milhas = pd.DataFrame(resultados_parseados)
            
            # Adiciona colunas calculadas
            if 'milhas' in df_milhas.columns:
                df_milhas['Custo Estimado (R$)'] = df_milhas['milhas'].apply(
                    lambda x: f"R$ {(x/1000 * custo_usuario_mil):,.2f}" if pd.notna(x) else "-"
                )
                
                if preco_cash_ref:
                    df_milhas['Valor/1k'] = df_milhas['milhas'].apply(
                        lambda x: f"R$ {(preco_cash_ref/x*1000):.2f}" if pd.notna(x) and x > 0 else "-"
                    )
                    df_milhas['Economia'] = df_milhas['milhas'].apply(
                        lambda x: f"{((preco_cash_ref - (x/1000*custo_usuario_mil))/preco_cash_ref*100):.0f}%" if pd.notna(x) and x > 0 else "-"
                    )
            
            # Renomeia colunas para exibição
            colunas_display = {
                'programa': 'Programa',
                'milhas': 'Milhas',
                'classe': 'Classe',
                'data': 'Data',
                'companhia': 'Cia',
                'paradas': 'Paradas',
                'assentos': 'Assentos',
                'Custo Estimado (R$)': 'Custo Est.',
                'Valor/1k': 'Valor/1k',
                'Economia': 'Economia'
            }
            
            df_display = df_milhas.rename(columns=colunas_display)
            
            # Seleciona apenas colunas existentes
            colunas_mostrar = [c for c in colunas_display.values() if c in df_display.columns]
            
            st.dataframe(df_display[colunas_mostrar], use_container_width=True, hide_index=True)
            
            # Encontra melhor opção
            melhor = min(resultados_parseados, key=lambda x: x.get('milhas', 999999))
            
            # Salva no histórico local
            historico_entry = {
                'data_busca': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'origem': busca_origem_milhas,
                'destino': busca_destino_milhas,
                'periodo': f"{data_inicio_str} - {data_fim_str}",
                'opcoes': len(resultados_parseados),
                'melhor_milhas': min([r.get('milhas', 999999) for r in resultados_parseados]),
                'melhor_programa': melhor.get('programa', 'N/A'),
                'resultados': resultados_parseados
            }
            st.session_state.historico_milhas.append(historico_entry)
            
            # Envia para o webhook (Google Sheets)
            if WEBHOOK_MILHAS_URL and "SUBSTITUIR" not in WEBHOOK_MILHAS_URL:
                try:
                    payload_webhook = {
                        "data_busca": historico_entry['data_busca'],
                        "origem": historico_entry['origem'],
                        "destino": historico_entry['destino'],
                        "periodo": historico_entry['periodo'],
                        "quantidade_opcoes": historico_entry['opcoes'],
                        "melhor_milhas": historico_entry['melhor_milhas'],
                        "melhor_programa": historico_entry['melhor_programa'],
                        "resultados_json": json.dumps(resultados_parseados, ensure_ascii=False)
                    }
                    response = requests.post(WEBHOOK_MILHAS_URL, json=payload_webhook, timeout=10)
                    if response.status_code == 200:
                        st.toast("✅ Histórico salvo!")
                except Exception as e:
                    pass  # Falha silenciosa para não atrapalhar UX
            
            st.divider()
            
            # Melhor opção destacada
            if resultados_parseados:
                st.markdown("#### 🏆 Melhor Opção")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Programa", melhor.get('programa', 'N/A'))
                with col2:
                    st.metric("Milhas", f"{melhor.get('milhas', 0):,}")
                with col3:
                    custo_melhor = (melhor.get('milhas', 0) / 1000) * custo_usuario_mil
                    st.metric("Custo Estimado", f"R$ {custo_melhor:,.2f}")
                
                if preco_cash_ref:
                    economia_melhor = preco_cash_ref - custo_melhor
                    if economia_melhor > 0:
                        st.success(f"✅ Usando {melhor.get('programa', 'milhas')}, você economiza **R$ {economia_melhor:,.2f}** comparado ao preço em dinheiro (R$ {preco_cash_ref:,.2f})")
                    else:
                        st.warning(f"💵 Para esta rota, pagar em dinheiro (R$ {preco_cash_ref:,.2f}) é mais vantajoso")
        
        else:
            st.warning("⚠️ Não foi possível extrair dados estruturados. Verifique o formato da resposta.")
            st.markdown("**Texto original:**")
            st.info(resultado_assistant)
        
        # Comparação com preço cash
        if df is not None and len(df) > 0 and preco_cash_ref:
            st.divider()
            st.markdown("#### 💵 Referência: Preço em Dinheiro")
            
            for classe in df_rota['Classe'].unique():
                df_classe = df_rota[df_rota['Classe'] == classe]
                if len(df_classe) > 0:
                    menor_preco = df_classe['Preço BRL'].min()
                    st.metric(
                        label=f"{classe}",
                        value=f"R$ {menor_preco:,.2f}",
                        help="Menor preço encontrado em dinheiro"
                    )
    
    st.divider()
    
    # Histórico de buscas
    if st.session_state.historico_milhas:
        with st.expander(f"📜 Histórico de Buscas desta Sessão ({len(st.session_state.historico_milhas)})"):
            for i, h in enumerate(reversed(st.session_state.historico_milhas[-10:])):  # Últimas 10
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                with col1:
                    st.write(f"**{h['origem']} → {h['destino']}**")
                with col2:
                    st.write(h['periodo'])
                with col3:
                    st.write(f"{h['opcoes']} opções")
                with col4:
                    st.write(f"{h['melhor_milhas']:,} mi")
                with col5:
                    st.write(h.get('melhor_programa', 'N/A'))
                st.caption(f"Busca em: {h['data_busca']}")
                st.divider()
            
            if st.button("🗑️ Limpar Histórico da Sessão"):
                st.session_state.historico_milhas = []
                st.rerun()
        
        # Info sobre persistência
        if "SUBSTITUIR" in WEBHOOK_MILHAS_URL:
            st.info("💡 Configure o webhook no Make.com para salvar o histórico permanentemente. Veja as instruções no código.")
    
    st.divider()
    
    # Calculadora manual (caso o parser não funcione)
    with st.expander("🧮 Calculadora Manual"):
        st.caption("Use se o parser automático não extrair os dados corretamente:")
        
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        with col_calc1:
            milhas_manual = st.number_input("Milhas necessárias", min_value=0, value=30000, step=1000, key="milhas_manual")
        with col_calc2:
            custo_manual = st.number_input("Custo por 1k milhas (R$)", min_value=0.0, value=20.0, step=1.0, key="custo_manual")
        with col_calc3:
            preco_cash_manual = st.number_input("Preço cash (R$)", min_value=0.0, value=3000.0, step=100.0, key="cash_manual")
        
        if milhas_manual > 0 and preco_cash_manual > 0:
            custo_total = (milhas_manual / 1000) * custo_manual
            valor_1k = (preco_cash_manual / milhas_manual) * 1000
            economia_manual = preco_cash_manual - custo_total
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Custo com milhas", f"R$ {custo_total:,.2f}")
            with col_r2:
                st.metric("Valor por 1k", f"R$ {valor_1k:.2f}")
            with col_r3:
                delta = f"{(economia_manual/preco_cash_manual*100):.0f}%"
                st.metric("Economia", f"R$ {economia_manual:,.2f}", delta)
    
    # Dicas
    with st.expander("💡 Dicas para usar o Seats.aero Assistant"):
        st.markdown("""
        **Como obter melhores resultados:**
        
        1. **Seja específico** - Inclua datas exatas e cabines desejadas
        2. **Flexibilidade** - Pergunte por datas alternativas próximas
        3. **Programas múltiplos** - O Assistant pode comparar vários programas
        4. **Conexões** - Pergunte sobre rotas alternativas com conexão
        
        **Programas com melhor disponibilidade Brasil → EUA:**
        - **Smiles** (GOL) - Boa disponibilidade, preços dinâmicos
        - **AAdvantage** - Tabela fixa, excelente valor em Business
        - **United MileagePlus** - Boa cobertura Star Alliance
        
        **Programas com melhor disponibilidade Brasil → Europa:**
        - **TAP Miles&Go** - Voos diretos Lisboa/Porto
        - **Flying Blue** - Air France/KLM via Paris/Amsterdam
        - **Iberia Plus** - Tabela fixa vantajosa
        
        **Perguntas úteis para o Assistant:**
        - "Qual o programa com menor custo em milhas para essa rota?"
        - "Tem disponibilidade em Business classe com milhas?"
        - "Quais datas têm mais disponibilidade nesse mês?"
        
        **Sobre os alertas:**
        - 🎉 **Oportunidade Excelente**: Valor > R$ 50/1k milhas em Business
        - ✅ **Boa Oportunidade**: Valor > R$ 35/1k milhas
        - 🚨 **Possível Erro de Tarifa**: Business por < 40k milhas (raro!)
        """)

# ============================================
# TAB 4: COMPARADOR DE MILHAS
# ============================================
with tab4:
    st.subheader("🎯 Comparador: Dinheiro vs. Milhas")
    
    df = load_flight_data()
    
    if df is not None and len(df) > 0:
        # Configurações do usuário
        st.markdown("### ⚙️ Seu Custo de Aquisição de Milhas")
        st.caption("Informe quanto você paga (em média) por 1.000 milhas em cada programa")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            custo_smiles = st.number_input("Smiles (R$/1k)", value=20.0, min_value=0.0, step=1.0)
        with col2:
            custo_aadvantage = st.number_input("AAdvantage (R$/1k)", value=25.0, min_value=0.0, step=1.0)
        with col3:
            custo_latam = st.number_input("LATAM Pass (R$/1k)", value=22.0, min_value=0.0, step=1.0)
        
        col4, col5, col6 = st.columns(3)
        with col4:
            custo_iberia = st.number_input("Iberia Plus (R$/1k)", value=22.0, min_value=0.0, step=1.0)
        with col5:
            custo_tap = st.number_input("TAP Miles&Go (R$/1k)", value=20.0, min_value=0.0, step=1.0)
        with col6:
            custo_azul = st.number_input("Azul (R$/1k)", value=18.0, min_value=0.0, step=1.0)
        
        custos_usuario = {
            "Smiles": custo_smiles,
            "AAdvantage": custo_aadvantage,
            "LATAM Pass": custo_latam,
            "Iberia Plus": custo_iberia,
            "TAP Miles&Go": custo_tap,
            "Azul Fidelidade": custo_azul,
        }
        
        st.divider()
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            rotas_disponiveis = df.apply(lambda x: f"{x['Origem']} → {x['Destino']}", axis=1).unique().tolist()
            rota_selecionada = st.selectbox("Selecione a rota:", rotas_disponiveis)
        with col2:
            classes_disponiveis = df['Classe'].unique().tolist()
            classe_selecionada = st.selectbox("Classe:", classes_disponiveis)
        
        if rota_selecionada:
            origem_sel, destino_sel = rota_selecionada.split(" → ")
            
            # Busca o voo mais barato para a rota/classe
            df_rota = df[(df['Origem'] == origem_sel) & (df['Destino'] == destino_sel) & (df['Classe'] == classe_selecionada)]
            
            if len(df_rota) > 0:
                voo_mais_barato = df_rota.loc[df_rota['Preço BRL'].idxmin()]
                preco_cash = voo_mais_barato['Preço BRL']
                
                st.divider()
                st.markdown(f"### 💵 Preço em Dinheiro: **R$ {preco_cash:,.2f}**")
                st.caption(f"{voo_mais_barato['Companhia Nome']} | {format_duration(voo_mais_barato['Duração'])} | {format_stops(voo_mais_barato['Paradas'])}")
                
                st.divider()
                st.markdown("### 🎫 Opções com Milhas")
                
                # Busca preços em milhas para a rota
                award_prices = get_award_prices(origem_sel, destino_sel)
                
                if award_prices:
                    classe_key = classe_selecionada.lower()
                    if classe_key == "economy":
                        classe_key = "economy"
                    elif classe_key == "business":
                        classe_key = "business"
                    elif classe_key == "first":
                        classe_key = "first"
                    else:
                        classe_key = "economy"
                    
                    comparacoes = []
                    
                    for programa, precos in award_prices.items():
                        milhas = precos.get(classe_key)
                        if milhas:
                            custo_usuario = custos_usuario.get(programa, 25.0)
                            custo_total_milhas = (milhas / 1000) * custo_usuario
                            valor_por_milha = calculate_value_per_mile(preco_cash, milhas)
                            economia = preco_cash - custo_total_milhas
                            economia_percent = (economia / preco_cash) * 100 if preco_cash > 0 else 0
                            vale_pena = custo_total_milhas < preco_cash
                            
                            comparacoes.append({
                                "programa": programa,
                                "milhas": milhas,
                                "custo_milhas": custo_total_milhas,
                                "valor_por_1k": valor_por_milha,
                                "economia": economia,
                                "economia_percent": economia_percent,
                                "vale_pena": vale_pena
                            })
                    
                    # Ordena por maior economia
                    comparacoes.sort(key=lambda x: x["economia"], reverse=True)
                    
                    for comp in comparacoes:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{comp['programa']}**")
                                st.caption(f"{comp['milhas']:,} milhas")
                            
                            with col2:
                                st.metric("Custo em R$", f"R$ {comp['custo_milhas']:,.2f}")
                            
                            with col3:
                                st.metric("Valor/1k milhas", f"R$ {comp['valor_por_1k']:.2f}")
                            
                            with col4:
                                if comp['vale_pena']:
                                    st.success(f"✅ Economia: {comp['economia_percent']:.0f}%")
                                else:
                                    st.error(f"❌ Prejuízo: {abs(comp['economia_percent']):.0f}%")
                            
                            st.divider()
                    
                    # Resumo
                    melhor_opcao = comparacoes[0] if comparacoes else None
                    if melhor_opcao and melhor_opcao['vale_pena']:
                        st.success(f"🏆 **Melhor opção:** {melhor_opcao['programa']} - Economia de R$ {melhor_opcao['economia']:,.2f} ({melhor_opcao['economia_percent']:.0f}%)")
                    elif melhor_opcao:
                        st.warning(f"💵 **Recomendação:** Pagar em dinheiro é mais vantajoso para esta rota.")
                else:
                    st.warning("Tabela de milhas não disponível para esta rota. Entre em contato para adicionar.")
            else:
                st.warning("Nenhum voo encontrado para esta rota/classe.")
    else:
        st.info("Faça uma busca primeiro na aba 'Nova Busca'.")
    
    st.divider()
    
    # Dicas
    with st.expander("💡 Dicas para maximizar suas milhas"):
        st.markdown("""
        **Regra de Ouro:** Nunca transfira pontos sem bônus de pelo menos 70%!
        
        **Custos de referência (R$ por 1.000 milhas):**
        - 🟢 Excelente: < R$ 18
        - 🟡 Bom: R$ 18-25
        - 🟠 Regular: R$ 25-35
        - 🔴 Caro: > R$ 35
        
        **Melhores formas de acumular:**
        1. Clubes de assinatura (Smiles, Azul) - menor custo por milha
        2. Transferências com bônus 100% - dobra seu poder de compra
        3. Promoções de compra direta - fique atento às ofertas
        
        **Programas com tabela fixa (melhor valor):**
        - AAdvantage (American Airlines)
        - Iberia Plus
        - TAP Miles&Go
        """)

# ============================================
# TAB 5: AEROPORTOS
# ============================================
with tab5:
    st.subheader("🛫 Consulta de Aeroportos")
    
    busca_aeroporto = st.text_input("Digite cidade, país ou código IATA:", placeholder="Ex: Paris, Brasil, JFK...")
    
    if busca_aeroporto:
        resultados = search_airports(busca_aeroporto)
        if resultados:
            df_aeroportos = pd.DataFrame(resultados)
            df_aeroportos.columns = ['Código IATA', 'Cidade', 'Aeroporto', 'País']
            st.dataframe(df_aeroportos, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum aeroporto encontrado.")
    else:
        st.info("Digite uma cidade, país ou código para buscar.")
    
    with st.expander("📋 Ver todos os aeroportos"):
        todos = [{"Código": k, "Cidade": v["cidade"], "Aeroporto": v["nome"], "País": v["pais"]} 
                 for k, v in sorted(AIRPORTS.items(), key=lambda x: x[1]['pais'])]
        st.dataframe(pd.DataFrame(todos), use_container_width=True, hide_index=True)

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "AirPoint © 2025 - Democratizando viagens com pontos e milhas"
    "</div>",
    unsafe_allow_html=True
)
