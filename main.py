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
pagina = st.sidebar.radio("Vai a:", ["Home", "Aggiungi Proprietà", "Aggiungi Immobile", "Lista Immobili"])

# --- PAGINA HOME ---
if pagina == "Home":
    st.title("🏠 Immobiliare Real Estate")
    st.write("Dashboard di gestione immobiliare.")
    st.info("Configurazione completata. Seleziona un'operazione dal menu a sinistra.")

# --- PAGINA AGGIUNGI PROPRIETÀ ---
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
        submit_p = st.form_submit_button("Salva Proprietà")

    if submit_p:
        if nome and cognome:
            try:
                supabase.table("proprieta").insert({"nome": nome, "cognome": cognome, "telefono": telefono, "email": email, "note": note}).execute()
                st.success(f"✅ {nome} {cognome} aggiunto con successo!")
            except Exception as e:
                st.error(f"Errore: {e}")
        else:
            st.warning("Nome e Cognome obbligatori.")

# --- PAGINA AGGIUNGI IMMOBILE ---
elif pagina == "Aggiungi Immobile":
    st.title("🏘️ Inserisci Nuovo Immobile")
    
    # 1. Recuperiamo i proprietari per il menu a tendina
    try:
        res_p = supabase.table("proprieta").select("id, nome, cognome").execute()
        lista_proprietari = res_p.data
        
        # Creiamo una lista di nomi leggibili e un dizionario per recuperare l'ID
        opzioni_proprietari = {f"{p['nome']} {p['cognome']}": p['id'] for p in lista_proprietari}
        
        if not opzioni_proprietari:
            st.warning("⚠️ Non ci sono proprietari nel database. Aggiungine uno prima di inserire un immobile.")
        else:
            with st.form("form_immobile", clear_on_submit=True):
                proprietario_scelto = st.selectbox("Seleziona la Proprietà", options=list(opzioni_proprietari.keys()))
                indirizzo = st.text_input("Indirizzo Immobile*")
                
                col1, col2 = st.columns(2)
                with col1:
                    citta = st.text_input("Città", value="Milano")
                    prezzo = st.number_input("Prezzo Richiesto (€)", min_value=0, step=1000)
                with col2:
                    tipo = st.selectbox("Tipo", ["Appartamento", "Villa", "Ufficio", "Box/Garage"])
                    stato = st.selectbox("Stato", ["Disponibile", "In trattativa", "Venduto"])
                
                descrizione = st.text_area("Descrizione breve")
                submit_i = st.form_submit_button("Salva Immobile")

            if submit_i:
                if indirizzo:
                    nuovo_immobile = {
                        "indirizzo": indirizzo,
                        "citta": citta,
                        "prezzo_richiesto": prezzo,
                        "tipo_immobile": tipo,
                        "stato_trattativa": stato,
                        "descrizione": descrizione,
                        "id_proprieta": opzioni_proprietari[proprietario_scelto] # Qui avviene la magia!
                    }
                    try:
                        supabase.table("immobili").insert(nuovo_immobile).execute()
                        st.success(f"✅ Immobile in {indirizzo} salvato e collegato correttamente!")
                    except Exception as e:
                        st.error(f"Errore durante il salvataggio: {e}")
                else:
                    st.warning("L'indirizzo è obbligatorio.")
    except Exception as e:
        st.error(f"Impossibile caricare i proprietari: {e}")

# --- PAGINA LISTA IMMOBILI ---
elif pagina == "Lista Immobili":
    st.title("📑 Elenco Completo")
    st.write("Qui vedremo presto la tabella riassuntiva di tutto l'inventario.")