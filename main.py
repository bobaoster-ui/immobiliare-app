import streamlit as st
from supabase import create_client, Client

# Configurazione della pagina
st.set_page_config(page_title="Immobiliare Real Estate", layout="wide", page_icon="🏠")

# Connessione a Supabase
@st.cache_resource
def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()

# --- SIDEBAR NAVIGAZIONE ---
st.sidebar.title("Menu")
pagina = st.sidebar.radio("Vai a:", ["Home", "Aggiungi Proprietà", "Lista Immobili"])

# --- PAGINA HOME ---
if pagina == "Home":
    st.title("🏠 Immobiliare Real Estate")
    st.write("Benvenuto nel pannello di gestione di Andrea.")
    st.info("Usa il menu a sinistra per inserire nuovi proprietari o gestire gli immobili.")

# --- PAGINA AGGIUNGI PROPRIETÀ ---
elif pagina == "Aggiungi Proprietà":
    st.title("👤 Nuova Proprietà")
    st.write("Inserisci i dati del proprietario dell'immobile.")

    with st.form("form_proprieta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome*")
            telefono = st.text_input("Telefono")
        with col2:
            cognome = st.text_input("Cognome*")
            email = st.text_input("Email")

        note = st.text_area("Note (es: orari per chiamare, esigenze particolari)")

        submit = st.form_submit_button("Salva Proprietà")

    if submit:
        if nome and cognome:
            nuovo_proprietario = {
                "nome": nome,
                "cognome": cognome,
                "telefono": telefono,
                "email": email,
                "note": note
            }
            try:
                res = supabase.table("proprieta").insert(nuovo_proprietario).execute()
                st.success(f"✅ {nome} {cognome} aggiunto con successo alla Proprietà!")
            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")
        else:
            st.warning("Per favore, inserisci almeno Nome e Cognome.")

# --- PAGINA LISTA IMMOBILI (BOZZA) ---
elif pagina == "Lista Immobili":
    st.title("📑 Elenco Immobili")
    st.info("Questa sezione verrà sviluppata nel prossimo step.")
