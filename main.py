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
# --- DASHBOARD (HOME) ---

# --- 1. QUI INIZIA LA DASHBOARD (Sotto il primo IF) ---
if pagina == "Dashboard":
    st.title("📊 Torre di Controllo Agenzia")
    
    # Tutto questo blocco è spostato di un TAB (4 spazi) a destra
    col1, col2, col3, col4 = st.columns(4)
    
    count_prop = len(supabase.table("proprieta").select("id").execute().data)
    count_imm = len(supabase.table("immobili").select("id").execute().data)
    count_cli = len(supabase.table("clienti").select("id").execute().data)
    count_app = len(supabase.table("appuntamenti").select("id").execute().data)

    col1.metric("🏠 Immobili", count_imm)
    col2.metric("👤 Proprietà", count_prop)
    col3.metric("🤝 Clienti", count_cli)
    col4.metric("📅 Visite Totali", count_app)

    st.divider()

    st.subheader("🕒 Prossime Visite in Agenda")
    res_dash = supabase.table("appuntamenti").select(
        "data_ora, esito, immobili(indirizzo), clienti(nome, cognome)"
    ).order("data_ora").execute()

    if res_dash.data:
        df_dash = pd.DataFrame(res_dash.data)
        df_dash['Data'] = pd.to_datetime(df_dash['data_ora'])
        df_dash['Orario'] = df_dash['Data'].dt.strftime('%d/%m/%Y %H:%M')
        df_dash['Immobile'] = df_dash['immobili'].apply(lambda x: x['indirizzo'] if x else "N/A")
        df_dash['Cliente'] = df_dash['clienti'].apply(lambda x: f"{x['nome']} {x['cognome']}" if x else "N/A")
        
        st.dataframe(
            df_dash[['Orario', 'Immobile', 'Cliente', 'esito']].head(5), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Non ci sono appuntamenti in programma.")

    st.divider()

    # 3. AZIONI RAPIDE
    st.subheader("⚡ Azioni Rapide")
    c_a, c_b, c_c = st.columns(3)
    if c_a.button("➕ Nuovo Immobile", use_container_width=True):
        st.info("Vai alla sezione Immobili dal menu a sinistra!")
    if c_b.button("📅 Fissa Appuntamento", use_container_width=True):
        st.info("Vai alla sezione Agenda dal menu a sinistra!")
    if c_c.button("📥 Esporta Dati", use_container_width=True):
        st.write("Funzione in arrivo...")

# --- PAGINA: PROPRIETÀ ---
elif pagina == "Proprietà (Venditori)":
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
        if not res_p.data:
            st.warning("Aggiungi prima un proprietario!")
        else:
            ops = {f"{p['nome']} {p['cognome']}": p['id'] for p in res_p.data}
            with st.form("i_form", clear_on_submit=True):
                prop = st.selectbox("Proprietario", options=list(ops.keys()))
                ind = st.text_input("Indirizzo*")
                prezzo = st.number_input("Prezzo (€)", min_value=0, step=5000)
                
                # --- NUOVO: Caricamento Foto ---
                uploaded_files = st.file_uploader("Carica foto dell'immobile", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
                
                if st.form_submit_button("Salva Immobile"):
                    # 1. Salva dati immobile
                    new_imm = supabase.table("immobili").insert({
                        "indirizzo": ind, 
                        "prezzo_richiesto": prezzo, 
                        "id_proprieta": ops[prop]
                    }).execute()
                    
                    imm_id = new_imm.data[0]['id']
                    
                    # 2. Carica le foto nello Storage
                    if uploaded_files:
                        for i, file in enumerate(uploaded_files):
                            # Creiamo un nome unico: ID_IMMO_0.jpg, ID_IMMO_1.jpg...
                            file_path = f"{imm_id}/foto_{i}.jpg"
                            supabase.storage.from_("foto_immobili").upload(file_path, file.getvalue())
                    
                    st.success("Immobile e foto salvati con successo!")

    with t2:
        res_i = supabase.table("immobili").select("*, proprieta(nome, cognome)").execute()
        if res_i.data:
            for imm in res_i.data:
                with st.expander(f"🏠 {imm['indirizzo']} - {imm['prezzo_richiesto']}€"):
                    st.write(f"Proprietario: {imm['proprieta']['nome']} {imm['proprieta']['cognome']}")
                    
                    # --- NUOVO: Recupero e Visualizzazione Galleria ---
                    files = supabase.storage.from_("foto_immobili").list(str(imm['id']))
                    if files:
                        cols = st.columns(3) # Griglia a 3 colonne
                        for idx, f_info in enumerate(files):
                            img_url = supabase.storage.from_("foto_immobili").get_public_url(f"{imm['id']}/{f_info['name']}")
                            cols[idx % 3].image(img_url, use_container_width=True)
                    else:
                        st.info("Nessuna foto disponibile per questo immobile.")
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

# --- PAGINA: AGENDA APPUNTAMENTI (Versione Rifinita) ---
elif pagina == "Agenda Appuntamenti":
    st.title("📅 Agenda Visite")
    t1, t2 = st.tabs(["➕ Nuova Visita", "📋 Calendario"])
    
    with t1:
        clienti_res = supabase.table("clienti").select("id, nome, cognome").execute()
        immobili_res = supabase.table("immobili").select("id, indirizzo").execute()
        
        if not clienti_res.data or not immobili_res.data:
            st.warning("Aggiungi prima clienti e immobili!")
        else:
            ops_c = {f"{c['nome']} {c['cognome']}": c['id'] for c in clienti_res.data}
            ops_i = {i['indirizzo']: i['id'] for i in immobili_res.data}

            with st.form("app_form", clear_on_submit=True):
                c_scelto = st.selectbox("Seleziona Cliente", options=list(ops_c.keys()))
                i_scelto = st.selectbox("Seleziona Immobile", options=list(ops_i.keys()))
                
                col_d, col_o, col_s = st.columns(3)
                data_app = col_d.date_input("Data", value=datetime.now(), format="DD/MM/YYYY")
                ora_app = col_o.time_input("Ora")
                # NUOVO CAMPO STATO
                stato_app = col_s.selectbox("Stato", ["In attesa", "Effettuato", "Annullato"])
                
                note_app = st.text_area("Note appuntamento")
                
                if st.form_submit_button("Fissa Appuntamento"):
                    dt_string = datetime.combine(data_app, ora_app).isoformat()
                    supabase.table("appuntamenti").insert({
                        "id_cliente": ops_c[c_scelto],
                        "id_immobile": ops_i[i_scelto],
                        "data_ora": dt_string,
                        "esito": stato_app, # Salviamo lo stato
                        "commenti": note_app
                    }).execute()
                    st.success(f"✅ Appuntamento registrato!")
                    st.balloons()            

    with t2:
            # Recuperiamo anche la colonna 'esito'
            res_app = supabase.table("appuntamenti").select("data_ora, esito, commenti, immobili(indirizzo), clienti(nome, cognome)").execute()
            if res_app.data:
                df_app = pd.DataFrame(res_app.data)
                df_app['Data e Ora'] = pd.to_datetime(df_app['data_ora']).dt.strftime('%d/%m/%Y %H:%M')
                df_app['Immobile'] = df_app['immobili'].apply(lambda x: x['indirizzo'] if x else "N/A")
                df_app['Cliente'] = df_app['clienti'].apply(lambda x: f"{x['nome']} {x['cognome']}" if x else "N/A")
                df_app = df_app.sort_values(by='data_ora', ascending=False)

                # Funzione per colorare lo Stato (Versione Socio Pro)
                def color_stato(val):
                    v = str(val).strip() # Toglie spazi bianchi fastidiosi
                    
                    if v == 'Effettuato': 
                        return 'background-color: #d4edda' # Verde
                    elif v == 'Annullato': 
                        return 'background-color: #f8d7da' # Rosso
                    elif v in ['In attesa', 'Da effettuare']: 
                        return 'background-color: #fff3cd' # Giallo
                    else: 
                        return '' # Nessun colore

                # Applichiamo lo stile
                df_styled = df_app[['Data e Ora', 'Immobile', 'Cliente', 'esito', 'commenti']].style.applymap(color_stato, subset=['esito'])
                
                st.dataframe(df_styled, use_container_width=True, hide_index=True)

# --- DASHBOARD (HOME) ---
else:
    st.title("🏠 Immobiliare Real Estate")
    st.write("Benvenuto socio! Ecco il polso della situazione:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Proprietari", len(supabase.table("proprieta").select("id").execute().data))
    c2.metric("Immobili", len(supabase.table("immobili").select("id").execute().data))
    c3.metric("Clienti", len(supabase.table("clienti").select("id").execute().data))