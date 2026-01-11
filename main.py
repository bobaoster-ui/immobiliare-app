import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# Configurazione
st.set_page_config(page_title="Immobiliare Real Estate", layout="wide", page_icon="🏠")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

supabase = init_connection()

# --- NAVIGAZIONE ---
st.sidebar.title("💎 Real Estate Pro")
pagina = st.sidebar.selectbox("Gestione:", 
    ["Dashboard", "Proprietà (Venditori)", "Immobili", "Clienti (Acquirenti)", "Agenda Appuntamenti"])

# --- DASHBOARD (HOME) ---
if pagina == "Dashboard":
    st.title("📊 Dashboard Agenzia")
    # Qui aggiungeremo i grafici e il riepilogo "bello"
    st.info("Benvenuto! Qui vedrai presto l'andamento delle vendite e gli appuntamenti di oggi.")

# --- SEZIONE PROPRIETÀ ---
elif pagina == "Proprietà (Venditori)":
    st.title("👤 Gestione Proprietà")
    tabs = st.tabs(["Aggiungi", "Elenco"])
    
    with tabs[0]:
        with st.form("p_form"):
            n = st.text_input("Nome*")
            c = st.text_input("Cognome*")
            t = st.text_input("Telefono")
            if st.form_submit_button("Salva"):
                supabase.table("proprieta").insert({"nome": n, "cognome": c, "telefono": t}).execute()
                st.success("Salvato!")
    
    with tabs[1]:
        res = supabase.table("proprieta").select("*").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data)[['nome', 'cognome', 'telefono']], use_container_width=True)

# --- SEZIONE IMMOBILI ---
elif pagina == "Immobili":
    st.title("🏘️ Gestione Immobili")
    tabs = st.tabs(["Aggiungi Immobile", "Catalogo Completo"])
    
    with tabs[0]:
        # Logica di inserimento (simile a quella fatta nel turno precedente)
        st.write("Modulo inserimento immobile...")
        # ... (codice inserimento immobile già testato)

    with tabs[1]:
        # Visualizzazione con JOIN (quella "intelligente" con i nomi dei proprietari)
        res = supabase.table("immobili").select("*, proprieta(nome, cognome)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)

# --- SEZIONE CLIENTI ---
elif pagina == "Clienti (Acquirenti)":
    st.title("🤝 Database Clienti")
    with st.form("c_form"):
        col1, col2 = st.columns(2)
        nome_c = col1.text_input("Nome Cliente*")
        cognome_c = col2.text_input("Cognome Cliente*")
        budget = st.number_input("Budget Massimo (€)", min_value=0)
        if st.form_submit_button("Registra Cliente"):
            supabase.table("clienti").insert({"nome": nome_c, "cognome": cognome_c, "budget_max": budget}).execute()
            st.success("Cliente registrato!")

# --- AGENDA APPUNTAMENTI ---
elif pagina == "Agenda Appuntamenti":
    st.title("📅 Agenda Visite")
    st.warning("Architettura pronta: qui Andrea incrocerà Clienti e Immobili.")
    # Prossimo step: il form per creare l'appuntamento