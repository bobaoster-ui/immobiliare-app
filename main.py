import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Immobiliare Real Estate", layout="wide", page_icon="🏠")

# Connessione a Supabase
@st.cache_resource
def init_connection():
    return create_client(st.secrets["supabase_url"], st.secrets["supabase_key"])

supabase = init_connection()

# --- NAVIGAZIONE ---
st.sidebar.title("💎 Real Estate Pro")
pagina = st.sidebar.selectbox("Gestione:", 
    ["Dashboard", "Proprietà (Venditori)", "Immobili", "Clienti (Acquirenti)", "Agenda Appuntamenti"])

# --- PAGINA: PROPRIETÀ ---
if pagina == "Proprietà (Venditori)":
    st.title("👤 Gestione Proprietà")
    t1, t2 = st.tabs(["➕ Aggiungi", "📋 Elenco"])
    with t1:
        with st.form("p_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            n = col1.text_input("Nome*")
            c = col2.text_input("Cognome*")
            tel = st.text_input("Telefono")
            if st.form_submit_button("Salva Proprietà"):
                if n and c:
                    supabase.table("proprieta").insert({"nome": n, "cognome": c, "telefono": tel}).execute()
                    st.success(f"Proprietà {n} {c} registrata!")
                else: st.error("Nome e Cognome obbligatori")
    with t2:
        res = supabase.table("proprieta").select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data)[['nome', 'cognome', 'telefono']], use_container_width=True, hide_index=True)

# --- PAGINA: IMMOBILI ---
elif pagina == "Immobili":
    st.title("🏘️ Gestione Immobili")
    t1, t2 = st.tabs(["➕ Aggiungi Immobile", "📋 Catalogo"])
    with t1:
        res_p = supabase.table("proprieta").select("id, nome, cognome").execute()
        if not res_p.data: st.warning("Aggiungi prima un proprietario!")
        else:
            ops = {f"{p['nome']} {p['cognome']}": p['id'] for p in res_p.data}
            with st.form("i_form", clear_on_submit=True):
                prop = st.selectbox("Proprietario", options=list(ops.keys()))
                ind = st.text_input("Indirizzo*")
                prezzo = st.number_input("Prezzo (€)", min_value=0, step=5000)
                if st.form_submit_button("Salva Immobile"):
                    supabase.table("immobili").insert({"indirizzo": ind, "prezzo_richiesto": prezzo, "id_proprieta": ops[prop]}).execute()
                    st.success("Immobile salvato!")
    with t2:
        res_i = supabase.table("immobili").select("*, proprieta(nome, cognome)").execute()
        if res_i.data:
            df_i = pd.DataFrame(res_i.data)
            df_i['Proprietario'] = df_i['proprieta'].apply(lambda x: f"{x['nome']} {x['cognome']}" if x else "N/A")
            st.dataframe(df_i[['indirizzo', 'prezzo_richiesto', 'Proprietario']], use_container_width=True, hide_index=True)

# --- PAGINA: CLIENTI ---
elif pagina == "Clienti (Acquirenti)":
    st.title("🤝 Database Clienti")
    t1, t2 = st.tabs(["➕ Registra Cliente", "📋 Lista Clienti"])
    with t1:
        with st.form("c_form", clear_on_submit=True): # Svuota maschera attivato!
            col1, col2 = st.columns(2)
            nc = col1.text_input("Nome*")
            cc = col2.text_input("Cognome*")
            bud = st.number_input("Budget (€)", min_value=0, step=10000)
            if st.form_submit_button("Registra Cliente"):
                if nc and cc:
                    supabase.table("clienti").insert({"nome": nc, "cognome": cc, "budget_max": bud}).execute()
                    st.success("Cliente registrato correttamente!")
    with t2:
        res_c = supabase.table("clienti").select("*").execute()
        if res_c.data: st.dataframe(pd.DataFrame(res_c.data)[['nome', 'cognome', 'budget_max']], use_container_width=True, hide_index=True)

# --- PAGINA: AGENDA APPUNTAMENTI ---
elif pagina == "Agenda Appuntamenti":
    st.title("📅 Agenda Visite")
    t1, t2 = st.tabs(["➕ Nuova Visita", "📋 Calendario"])
    
    with t1:
        # Recuperiamo dati per i menu a tendina
        clienti_res = supabase.table("clienti").select("id, nome, cognome").execute()
        immobili_res = supabase.table("immobili").select("id, indirizzo").execute()
        
        if not clienti_res.data or not immobili_res.data:
            st.warning("Assicurati di avere almeno un cliente e un immobile nel database.")
        else:
            ops_c = {f"{c['nome']} {c['cognome']}": c['id'] for c in clienti_res.data}
            ops_i = {i['indirizzo']: i['id'] for i in immobili_res.data}
            
            with st.form("app_form", clear_on_submit=True):
                c_scelto = st.selectbox("Seleziona Cliente", options=list(ops_c.keys()))
                i_scelto = st.selectbox("Seleziona Immobile", options=list(ops_i.keys()))
                data_app = st.date_input("Data Appuntamento", value=datetime.now())
                ora_app = st.time_input("Ora Appuntamento")
                note_app = st.text_area("Note appuntamento")
                
                if st.form_submit_button("Fissa Appuntamento"):
                    dt_string = datetime.combine(data_app, ora_app).isoformat()
                    supabase.table("appuntamenti").insert({
                        "id_cliente": ops_c[c_scelto],
                        "id_immobile": ops_i[i_scelto],
                        "data_ora": dt_string,
                        "commenti": note_app
                    }).execute()
                    st.success(f"Appuntamento fissato per {c_scelto} in {i_scelto}!")

    with t2:
        # Visualizzazione con doppio Join (Immobile + Cliente)
        res_app = supabase.table("appuntamenti").select("data_ora, commenti, immobili(indirizzo), clienti(nome, cognome)").execute()
        if res_app.data:
            df_app = pd.DataFrame(res_app.data)
            df_app['Data e Ora'] = pd.to_datetime(df_app['data_ora']).dt.strftime('%d/%m/%Y %H:%M')
            df_app['Immobile'] = df_app['immobili'].apply(lambda x: x['indirizzo'] if x else "N/A")
            df_app['Cliente'] = df_app['clienti'].apply(lambda x: f"{x['nome']} {x['cognome']}" if x else "N/A")
            st.dataframe(df_app[['Data e Ora', 'Immobile', 'Cliente', 'commenti']], use_container_width=True, hide_index=True)

# --- DASHBOARD (HOME) ---
else:
    st.title("🏠 Immobiliare Real Estate")
    st.write("Benvenuto socio! Ecco il polso della situazione:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Proprietari", len(supabase.table("proprieta").select("id").execute().data))
    c2.metric("Immobili", len(supabase.table("immobili").select("id").execute().data))
    c3.metric("Clienti", len(supabase.table("clienti").select("id").execute().data))