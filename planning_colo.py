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

st.header("2. Paramètres colo")
nb_jours = st.number_input("Nombre de jours", 1, 30, value=config_chargee.get("nb_jours", 5))
liste_jours = list(range(1, nb_jours + 1))

st.header("3. Liste des tâches")
taches_input = st.text_area("Une tâche par ligne (ex: Vaisselle (2))", 
                           value="Nettoyage Matin (2)\nVaisselle Midi (4)\nCuisine Soir (3)\nCourse (2)")
taches_brutes = [t.strip() for t in taches_input.split("\n") if t.strip()]

# Dictionnaire pour stocker les réglages
config_taches = {}
for i, tache in enumerate(taches_brutes):
    nom = tache.split('(')[0].strip()
    col1, col2 = st.columns(2)
    with col1:
        nb = st.number_input(f"👥 {nom} : nb personnes", 1, max(1, len(prenoms)), 1, key=f"nb_{i}")
    with col2:
        jours = st.multiselect(f"📅 Jours pour {nom}", liste_jours, default=liste_jours, key=f"j_{i}")
    config_taches[nom] = {"nb": nb, "jours": jours}

# =====================
# GÉNÉRATION
# =====================
if st.button("GÉNÉRER LE PLANNING", use_container_width=True):
    if not prenoms or not taches_brutes:
        st.error("Ajoutez des jeunes et des tâches !")
        st.stop()

    planning_data = []
    historique_taches = {e: [] for e in prenoms}
    nb_taches_par_jeune = {e: 0 for e in prenoms}

    for jour in liste_jours:
        pris_ce_jour = set()
        
        for nom_tache, cfg in config_taches.items():
            if jour not in cfg["jours"]:
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": "-"})
                continue
            
            besoin = cfg["nb"]
            
            # Tri intelligent
            def score(jeune):
                # Pénalité si fait la veille
                penalite = 100 if (historique_taches[jeune] and historique_taches[jeune][-1] == nom_tache) else 0
                return (penalite, nb_taches_par_jeune[jeune], random.random())

            candidats = [e for e in prenoms if e not in pris_ce_jour]
            candidats.sort(key=score)
            
            assignes = candidats[:besoin]
            
            for e in assignes:
                pris_ce_jour.add(e)
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(nom_tache)
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": e})

    # =====================
    # AFFICHAGE FINAL
    # =====================
    df = pd.DataFrame(planning_data)
    
    # Création du pivot trié
    pivot_df = df.pivot_table(
        index="Tâche", 
        columns="Jour", 
        values="Jeune", 
        aggfunc=lambda x: "<br>".join([str(i) for i in x if i != "-"]),
        fill_value="-"
    )
    
    # S'assurer que les colonnes de jours sont bien triées
    pivot_df = pivot_df.sort_index(axis=1)
    
    st.success("Planning généré !")
    st.write(pivot_df.to_html(escape=False), unsafe_allow_html=True)
    
    st.subheader("📊 Équilibre")
    st.bar_chart(pd.Series(nb_taches_par_jeune))

    # Export
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Télécharger CSV", csv, "planning.csv", "text/csv")
