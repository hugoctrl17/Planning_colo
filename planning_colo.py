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
nb_jours = st.number_input("Nombre de jours", 1, 30, value=config_chargee.get("nb_jours", 14))
liste_jours = list(range(1, nb_jours + 1))

st.header("3. Liste des tâches")
taches_input = st.text_area("Une tâche par ligne (ex: Vaisselle (2))", 
                           value="Nettoyage Matin (2)\nVaisselle Midi (4)\nCuisine Soir (3)\nCourse (2)")
taches_brutes = [t.strip() for t in taches_input.split("\n") if t.strip()]

# Configuration des tâches
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
        # Suivi du nombre de tâches faites ce jour par chaque jeune
        taches_ce_jour = {e: 0 for e in prenoms}
        
        for nom_tache, cfg in config_taches.items():
            if jour not in cfg["jours"]:
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": "-"})
                continue
            
            besoin = cfg["nb"]
            
            def score(jeune):
                # 1. Pénalité forte si tâche faite la veille
                penalite_veille = 100 if (historique_taches[jeune] and historique_taches[jeune][-1] == nom_tache) else 0
                # 2. Pénalité modérée si a déjà une tâche aujourd'hui
                penalite_deja_pris = 50 if taches_ce_jour[jeune] > 0 else 0
                # 3. Équité globale
                total = nb_taches_par_jeune[jeune]
                return (penalite_veille, penalite_deja_pris, total, random.random())

            # Tous les jeunes sont candidats, triés par score
            candidats = sorted(prenoms, key=score)
            assignes = candidats[:besoin]
            
            for e in assignes:
                taches_ce_jour[e] += 1
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(nom_tache)
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": e})

    # =====================
    # AFFICHAGE FINAL
    # =====================
    df = pd.DataFrame(planning_data)
    
    # Pivot pour tableau à double entrée
    # L'aggfunc combine les prénoms par saut de ligne HTML
    pivot_df = df.pivot_table(
        index="Tâche", 
        columns="Jour", 
        values="Jeune", 
        aggfunc=lambda x: "<br>".join([str(i) for i in x if i != "-"]),
        fill_value="-"
    )
    
    # Tri des jours
    pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1)
    
    st.success("Planning généré avec succès !")
    # Rendu HTML pour afficher les noms les uns sous les autres
    st.write(pivot_df.to_html(escape=False), unsafe_allow_html=True)
    
    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Télécharger CSV", csv, "planning.csv", "text/csv")
