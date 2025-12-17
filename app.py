import streamlit as st
import requests
from datetime import date, timedelta

# Configuração da página
st.set_page_config(
    page_title="AirPoint - Busca de Voos",
    page_icon="✈️",
    layout="centered"
)

# URL do Webhook (Make)
WEBHOOK_URL = "https://hook.us2.make.com/ewd1k1ngiulmplmb8gitlsio1xztpikx"

# Header
st.title("✈️ AirPoint - Busca de Voos")
st.markdown("Pesquise passagens aéreas e salve os resultados automaticamente.")

st.divider()

# Formulário de busca
col1, col2 = st.columns(2)

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

# Data com mínimo de amanhã
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
        with st.spinner("Buscando voos..."):
            try:
                params = {
                    "origin": origem,
                    "destination": destino,
                    "date": data_voo.strftime("%Y-%m-%d")
                }
                
                response = requests.get(WEBHOOK_URL, params=params, timeout=30)
                
                if response.status_code == 200:
                    st.success(f"✅ Busca realizada com sucesso!")
                    st.info(f"**Rota:** {origem} → {destino}  \n**Data:** {data_voo.strftime('%d/%m/%Y')}")
                    st.markdown("Os resultados foram salvos na planilha do Google Sheets.")
                else:
                    st.error(f"❌ Erro na busca (código {response.status_code})")
                    
            except requests.exceptions.Timeout:
                st.warning("⏱️ A busca está demorando mais que o esperado. Verifique a planilha em alguns minutos.")
            except Exception as e:
                st.error(f"❌ Erro ao conectar: {str(e)}")

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "AirPoint © 2025 - Democratizando viagens com pontos e milhas"
    "</div>",
    unsafe_allow_html=True
)
