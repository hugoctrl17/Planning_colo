import streamlit as st
import pandas as pd
import json
import random

# =====================
# CONFIGURATION
# =====================
st.set_page_config(page_title="Planning Colo", layout="wide")
st.title("📅 Générateur de Planning Colo (Optimisé)")

# Sidebar pour configuration
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
    memo_taches_faites = {e: set() for e in prenoms}
    nb_taches_par_jeune = {e: 0 for e in prenoms}

    for jour in liste_jours:
        taches_ce_jour = {e: 0 for e in prenoms}
        
        for nom_tache, cfg in config_taches.items():
            if jour not in cfg["jours"]:
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": "-"})
                continue
            
            besoin = cfg["nb"]
            
            def score(jeune):
                # 1. PRIORITÉ : N'a jamais fait cette tâche ?
                a_deja_fait = nom_tache in memo_taches_faites[jeune]
                priorite_couverture = 0 if not a_deja_fait else 1
                # 2. Pénalité : fait la veille
                penalite_veille = 1 if (historique_taches[jeune] and historique_taches[jeune][-1] == nom_tache) else 0
                # 3. Pénalité : déjà une tâche aujourd'hui
                penalite_deja_pris = 1 if taches_ce_jour[jeune] > 0 else 0
                # 4. Équité globale
                total = nb_taches_par_jeune[jeune]
                return (priorite_couverture, penalite_veille, penalite_deja_pris, total, random.random())

            candidats = sorted(prenoms, key=score)
            assignes = candidats[:besoin]
            
            for e in assignes:
                taches_ce_jour[e] += 1
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(nom_tache)
                memo_taches_faites[e].add(nom_tache)
                planning_data.append({"Jour": jour, "Tâche": nom_tache, "Jeune": e})

    # =====================
    # AFFICHAGE
    # =====================
    df = pd.DataFrame(planning_data)
    
    # Planning Double Entrée
    pivot_df = df.pivot_table(index="Tâche", columns="Jour", values="Jeune", 
                              aggfunc=lambda x: "<br>".join([str(i) for i in x if i != "-"]), fill_value="-")
    pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1)
    
    st.success("Planning généré !")
    st.write(pivot_df.to_html(escape=False), unsafe_allow_html=True)
    
    # Statistiques
    st.subheader("📊 Récapitulatif : Tâches par jeune")
    recap_df = df[df["Jeune"] != "-"].pivot_table(index="Jeune", columns="Tâche", aggfunc="size", fill_value=0)
    recap_df["Total"] = recap_df.sum(axis=1)
    st.dataframe(recap_df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Télécharger CSV", csv, "planning.csv", "text/csv")
