import streamlit as st
import pandas as pd
import json
import random

# =====================
# CONFIGURATION
# =====================
st.set_page_config(page_title="Planning Colo", layout="wide")
st.title("📅 Générateur de Planning Colo")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Charger une config (JSON)", type=["json"])
    config_chargee = json.load(uploaded_file) if uploaded_file else {}

# Entrées
st.header("1. Liste des jeunes")
prenoms_input = st.text_area("Un prénom par ligne", value="\n".join(config_chargee.get("prenoms", ["Emma", "Léo", "Noah", "Jade", "Lucas"])))
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

st.header("2. Paramètres colo")
nb_jours = st.number_input("Nombre de jours", 1, 30, value=config_chargee.get("nb_jours", 5))
liste_jours = list(range(1, nb_jours + 1))

st.header("3. Liste des tâches")
taches_input = st.text_area("Une tâche par ligne (ex: Vaisselle (2))", 
                           value="Nettoyage Matin (2)\nVaisselle Midi (4)\nCuisine Soir (3)\nCourse (2)")
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# Paramètres par tâche
nb_personnes = {}
jours_par_tache = {}

# MODIFICATION ICI : On utilise i pour garantir une clé unique
for i, tache in enumerate(taches):
    nom_tache = tache.split('(')[0].strip()
    col1, col2 = st.columns(2)
    with col1:
        # Clé unique avec l'index i
        nb_personnes[nom_tache] = st.number_input(f"👥 {nom_tache} : nb personnes", 1, max(1, nb_enfants), 1, key=f"nb_{i}")
    with col2:
        # Clé unique avec l'index i
        jours_par_tache[nom_tache] = st.multiselect(f"📅 Jours pour {nom_tache}", liste_jours, default=liste_jours, key=f"j_{i}")

# =====================
# GÉNÉRATION
# =====================
if st.button("GÉNÉRER LE PLANNING", use_container_width=True):
    if not prenoms or not taches:
        st.error("Ajoutez des jeunes et des tâches !")
        st.stop()

    planning = []
    historique_taches = {e: [] for e in prenoms}
    nb_taches_par_jeune = {e: 0 for e in prenoms}

    for jour in liste_jours:
        pris_ce_jour = set()
        
        for tache in jours_par_tache:
            if jour not in jours_par_tache[tache]: continue
            
            besoin = nb_personnes[tache]
            
            def score_candidat(jeune):
                a_fait_hier = 100 if (len(historique_taches[jeune]) > 0 and historique_taches[jeune][-1] == tache) else 0
                nb_total = nb_taches_par_jeune[jeune]
                return (a_fait_hier, nb_total, random.random())

            candidats = [e for e in prenoms if e not in pris_ce_jour]
            candidats.sort(key=score_candidat)
            assignes = candidats[:besoin]
            
            for e in assignes:
                pris_ce_jour.add(e)
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(tache)
                planning.append({"Jour": f"Jour {jour}", "Tâche": tache, "Jeune": e})

    # RÉSULTATS
    df = pd.DataFrame(planning)
    st.success("Planning généré avec succès !")
    
    pivot_df = df.pivot_table(
        index="Tâche", 
        columns="Jour", 
        values="Jeune", 
        aggfunc=lambda x: "<br>".join(x)
    ).fillna("-")
    
    st.subheader("📅 Planning détaillé")
    st.write(pivot_df.to_html(escape=False), unsafe_allow_html=True)
    
    st.subheader("📊 Équilibre (Nb de tâches par jeune)")
    st.bar_chart(pd.Series(nb_taches_par_jeune))

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Télécharger CSV", csv, "planning.csv", "text/csv")
