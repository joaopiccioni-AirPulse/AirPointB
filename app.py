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

# Função para carregar dados da planilha
@st.cache_data(ttl=30)  # Cache de 30 segundos
def load_flight_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['Data Busca', 'Origem', 'Destino', 'Data Voo', 'Companhia', 'Classe', 'Preço BRL', 'Duração']
        df['Preço BRL'] = pd.to_numeric(df['Preço BRL'], errors='coerce')
        return df
    except Exception as e:
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

# Header
st.title("✈️ AirPoint - Busca de Voos")
st.markdown("Pesquise passagens aéreas e compare preços em tempo real.")

st.divider()

# Tabs
tab1, tab2 = st.tabs(["🔍 Nova Busca", "📊 Resultados"])

with tab1:
    # Formulário de busca
    col1, col2, col3 = st.columns(3)

    with col1:
        origem = st.text_input(
            "Origem (código IATA)",
            value="GRU",
            max_chars=3,
            help="Ex: GRU, CGH, GIG, BSB"
        ).upper()

    with col2:
        destino = st.text_input(
            "Destino (código IATA)",
            value="MIA",
            max_chars=3,
            help="Ex: MIA, JFK, LIS, CDG"
        ).upper()

    with col3:
        data_minima = date.today() + timedelta(days=1)
        data_voo = st.date_input(
            "Data do Voo",
            value=data_minima + timedelta(days=30),
            min_value=data_minima,
            help="Selecione a data de partida"
        )

    st.divider()

    # Botão de busca
    if st.button("🔍 Buscar Voos", type="primary", use_container_width=True):
        
        # Validações
        if len(origem) != 3:
            st.error("❌ Código de origem deve ter 3 letras (ex: GRU)")
        elif len(destino) != 3:
            st.error("❌ Código de destino deve ter 3 letras (ex: MIA)")
        elif origem == destino:
            st.error("❌ Origem e destino não podem ser iguais")
        else:
            # Dispara o webhook
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
                        
                        # Aguarda processamento
                        with st.spinner("Processando resultados..."):
                            time.sleep(5)
                        
                        # Limpa cache e redireciona para resultados
                        st.cache_data.clear()
                        st.info("👆 Clique na aba **Resultados** para ver os voos encontrados.")
                    else:
                        st.error(f"❌ Erro na busca (código {response.status_code})")
                        
                except requests.exceptions.Timeout:
                    st.warning("⏱️ Busca em andamento. Aguarde alguns segundos e veja a aba Resultados.")
                except Exception as e:
                    st.error(f"❌ Erro ao conectar: {str(e)}")

with tab2:
    # Botão para atualizar dados
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
    
    # Carrega dados
    df = load_flight_data()
    
    if df is not None and len(df) > 0:
        # Filtros
        st.subheader("Filtros")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            origens = ['Todas'] + sorted(df['Origem'].unique().tolist())
            filtro_origem = st.selectbox("Origem", origens)
        
        with col2:
            destinos = ['Todos'] + sorted(df['Destino'].unique().tolist())
            filtro_destino = st.selectbox("Destino", destinos)
        
        with col3:
            classes = ['Todas'] + sorted(df['Classe'].unique().tolist())
            filtro_classe = st.selectbox("Classe", classes)
        
        # Aplica filtros
        df_filtrado = df.copy()
        if filtro_origem != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Origem'] == filtro_origem]
        if filtro_destino != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Destino'] == filtro_destino]
        if filtro_classe != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Classe'] == filtro_classe]
        
        st.divider()
        
        if len(df_filtrado) > 0:
            # Resumo: Mais barato e Mais rápido por classe
            st.subheader("🏆 Melhores Opções")
            
            classes_disponiveis = df_filtrado['Classe'].unique()
            
            for classe in classes_disponiveis:
                df_classe = df_filtrado[df_filtrado['Classe'] == classe].copy()
                
                if len(df_classe) > 0:
                    # Mais barato
                    mais_barato = df_classe.loc[df_classe['Preço BRL'].idxmin()]
                    
                    # Mais rápido
                    df_classe['Duracao_Min'] = df_classe['Duração'].apply(duration_to_minutes)
                    mais_rapido = df_classe.loc[df_classe['Duracao_Min'].idxmin()]
                    
                    st.markdown(f"### {classe}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            label=f"💰 Mais Barato ({mais_barato['Companhia']})",
                            value=f"R$ {mais_barato['Preço BRL']:,.2f}",
                            help=f"Duração: {format_duration(mais_barato['Duração'])}"
                        )
                        st.caption(f"Duração: {format_duration(mais_barato['Duração'])} | {mais_barato['Origem']} → {mais_barato['Destino']} | {mais_barato['Data Voo']}")
                    
                    with col2:
                        st.metric(
                            label=f"⚡ Mais Rápido ({mais_rapido['Companhia']})",
                            value=format_duration(mais_rapido['Duração']),
                            help=f"Preço: R$ {mais_rapido['Preço BRL']:,.2f}"
                        )
                        st.caption(f"Preço: R$ {mais_rapido['Preço BRL']:,.2f} | {mais_rapido['Origem']} → {mais_rapido['Destino']} | {mais_rapido['Data Voo']}")
                    
                    st.divider()
            
            # Tabela completa
            st.subheader("📋 Todos os Voos")
            
            # Formata para exibição
            df_display = df_filtrado.copy()
            df_display['Preço BRL'] = df_display['Preço BRL'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['Duração'] = df_display['Duração'].apply(format_duration)
            
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

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "AirPoint © 2025 - Democratizando viagens com pontos e milhas"
    "</div>",
    unsafe_allow_html=True
)
