import streamlit as st
import pandas as pd
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
pagina = st.sidebar.radio("Vai a:", ["Home", "Aggiungi Proprietà", "Aggiungi Immobile", "Lista Immobili"])

# --- FUNZIONE DI SUPPORTO: CARICA PROPRIETARI ---
def get_proprietari():
    res = supabase.table("proprieta").select("id, nome, cognome").execute()
    return res.data

# --- PAGINE PRECEDENTI (Invariate per brevità, mantieni il codice di prima) ---
if pagina == "Home":
    st.title("🏠 Immobiliare Real Estate")
    st.write("Benvenuto socio! Ecco il riepilogo della tua agenzia.")
    
    # Piccola anteprima veloce
    try:
        count_imm = supabase.table("immobili").select("*", count="exact").execute()
        count_prop = supabase.table("proprieta").select("*", count="exact").execute()
        col1, col2 = st.columns(2)
        col1.metric("Totale Immobili", count_imm.count)
        col2.metric("Totale Proprietari", count_prop.count)
    except:
        st.write("Inizia ad aggiungere dati per vedere le statistiche!")

elif pagina == "Aggiungi Proprietà":
    st.title("👤 Nuova Proprietà")
    with st.form("form_proprieta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome*")
            telefono = st.text_input("Telefono")
        with col2:
            cognome = st.text_input("Cognome*")
            email = st.text_input("Email")
        note = st.text_area("Note")
        if st.form_submit_button("Salva Proprietà"):
            if nome and cognome:
                supabase.table("proprieta").insert({"nome": nome, "cognome": cognome, "telefono": telefono, "email": email, "note": note}).execute()
                st.success("Proprietà salvata!")
            else:
                st.warning("Inserisci i campi obbligatori.")

elif pagina == "Aggiungi Immobile":
    st.title("🏘️ Inserisci Nuovo Immobile")
    lista_p = get_proprietari()
    if not lista_p:
        st.warning("Aggiungi prima un proprietario!")
    else:
        opzioni = {f"{p['nome']} {p['cognome']}": p['id'] for p in lista_p}
        with st.form("form_immobile", clear_on_submit=True):
            prop_scelto = st.selectbox("Seleziona la Proprietà", options=list(opzioni.keys()))
            indirizzo = st.text_input("Indirizzo*")
            col1, col2 = st.columns(2)
            with col1:
                citta = st.text_input("Città", value="Milano")
                prezzo = st.number_input("Prezzo (€)", min_value=0)
            with col2:
                tipo = st.selectbox("Tipo", ["Appartamento", "Villa", "Ufficio", "Box"])
                stato = st.selectbox("Stato", ["Disponibile", "In trattativa", "Venduto"])
            if st.form_submit_button("Salva Immobile"):
                if indirizzo:
                    data = {"indirizzo": indirizzo, "citta": citta, "prezzo_richiesto": prezzo, "tipo_immobile": tipo, "stato_trattativa": stato, "id_proprieta": opzioni[prop_scelto]}
                    supabase.table("immobili").insert(data).execute()
                    st.success("Immobile salvato!")

# --- NUOVA PAGINA LISTA IMMOBILI ---
elif pagina == "Lista Immobili":
    st.title("📑 Elenco Immobili e Proprietà")

    try:
        # Recuperiamo gli immobili uniti ai dati della proprietà (Join)
        res = supabase.table("immobili").select("*, proprieta(nome, cognome, telefono)").execute()
        
        if not res.data:
            st.info("Non ci sono ancora immobili registrati.")
        else:
            # Trasformiamo i dati in un DataFrame per una visualizzazione migliore
            df = pd.DataFrame(res.data)
            
            # Pulizia: estraiamo nome e cognome dalla colonna 'proprieta' (che è un dizionario)
            df['Proprietario'] = df['proprieta'].apply(lambda x: f"{x['nome']} {x['cognome']}" if x else "N/A")
            df['Contatto'] = df['proprieta'].apply(lambda x: x['telefono'] if x else "N/A")
            
            # Selezioniamo e rinominiamo le colonne per l'utente finale
            df_display = df[['indirizzo', 'citta', 'tipo_immobile', 'prezzo_richiesto', 'stato_trattativa', 'Proprietario', 'Contatto']]
            df_display.columns = ['Indirizzo', 'Città', 'Tipologia', 'Prezzo (€)', 'Stato', 'Proprietà', 'Telefono']

            # Filtro rapido in alto
            stato_filtro = st.multiselect("Filtra per stato:", options=df_display['Stato'].unique(), default=df_display['Stato'].unique())
            df_filtrato = df_display[df_display['Stato'].isin(stato_filtro)]

            st.dataframe(df_filtrato, use_container_width=True, hide_index=True)
            
            st.download_button(label="Scarica Excel (CSV)", data=df_filtrato.to_csv(index=False), file_name="lista_immobili.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Errore nel caricamento della lista: {e}")