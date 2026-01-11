import streamlit as st
from supabase import create_client, Client

# Configurazione della pagina
st.set_page_config(page_title="Immobiliare Real Estate", layout="wide", page_icon="🏠")

# Funzione per connettersi a Supabase usando i Secrets di Streamlit
@st.cache_resource
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Errore nella lettura dei Secrets: {e}")
    st.stop()

st.title("🏠 Immobiliare Real Estate")
st.sidebar.success("Connesso al Database")

# --- TEST CONNESSIONE ---
st.subheader("Verifica Tabelle")

col1, col2 = st.columns(2)

with col1:
    try:
        # Proviamo a leggere la tabella Proprietà
        res_prop = supabase.table("proprieta").select("*").limit(1).execute()
        st.success("✅ Tabella 'Proprietà' trovata!")
    except Exception as e:
        st.error(f"❌ Errore tabella Proprietà: {e}")

with col2:
    try:
        # Proviamo a leggere la tabella Immobili
        res_imm = supabase.table("immobili").select("*").limit(1).execute()
        st.success("✅ Tabella 'Immobili' trovata!")
    except Exception as e:
        st.error(f"❌ Errore tabella Immobili: {e}")

st.info("Socio, se vedi i messaggi verdi qui sopra, il database è pronto per accogliere i dati di Andrea!")
