# AirPoint - Dashboard de Busca de Voos

Dashboard para pesquisar passagens aéreas via API Amadeus.

## Deploy no Streamlit Cloud (Gratuito)

### Passo 1: Subir para o GitHub

1. Crie um repositório no GitHub (ex: `airpoint-dashboard`)
2. Faça upload dos arquivos `app.py` e `requirements.txt`

### Passo 2: Conectar ao Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em "New app"
3. Conecte sua conta GitHub
4. Selecione o repositório `airpoint-dashboard`
5. Branch: `main`
6. Main file path: `app.py`
7. Clique em "Deploy"

### Passo 3: Pronto!

Em ~2 minutos você terá uma URL pública tipo:
```
https://airpoint-dashboard.streamlit.app
```

## Configuração

Para alterar a URL do webhook, edite a linha no `app.py`:

```python
WEBHOOK_URL = "https://hook.us2.make.com/SEU_WEBHOOK_AQUI"
```

## Rodar Localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
