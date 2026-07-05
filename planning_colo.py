import streamlit as st
import pandas as pd
import json

# =====================
# CONFIGURATION
# =====================
st.set_page_config(page_title="Planning Colo", layout="centered")
st.title("📅 Générateur de Planning Colo")

# =====================
# SIDEBAR / CONFIGURATION
# =====================
uploaded_file = st.sidebar.file_uploader("Charger une config (JSON)", type=["json"])
config_chargee = json.load(uploaded_file) if uploaded_file else {}

st.header("1. Liste des jeunes")
prenoms_input = st.text_area("Un prénom par ligne", value="\n".join(config_chargee.get("prenoms", ["Emma", "Léo", "Noah"])))
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

st.header("2. Paramètres colo")
nb_jours = st.number_input("Nombre de jours", 1, 30, value=config_chargee.get("nb_jours", 5))
liste_jours = list(range(1, nb_jours + 1))

st.header("3. Liste des tâches")
taches_input = st.text_area("Une tâche par ligne (ex: Vaisselle (2))", 
                           value="Nettoyage Matin (2)\nVaisselle Midi (4)\nCuisine Soir (3)")
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# =====================
# PARAMÈTRES PAR TÂCHE
# =====================
nb_personnes = {}
jours_par_tache = {}

for tache in taches:
    nom_tache = tache.split('(')[0].strip()
    col1, col2 = st.columns(2)
    with col1:
        nb_personnes[nom_tache] = st.number_input(f"👥 {nom_tache} : nb personnes", 1, max(1, nb_enfants), 1)
    with col2:
        jours_par_tache[nom_tache] = st.multiselect(f"📅 Jours pour {nom_tache}", liste_jours, default=liste_jours)

# =====================
# LOGIQUE DE GÉNÉRATION
# =====================
def peut_faire_tache(enfant, tache, historique):
    """Vérifie si le jeune peut faire la tâche (pas 2 fois la même sur les 2 derniers jours)."""
    h = historique[enfant]
    if len(h) < 2: return True
    return not (h[-1] == tache and h[-2] == tache)

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
            
            # Filtre les candidats disponibles et respectant la contrainte de roulement
            candidats = [e for e in prenoms if e not in pris_ce_jour and peut_faire_tache(e, tache, historique_taches)]
            
            # Si pénurie, on ignore la contrainte de roulement
            if len(candidats) < besoin:
                candidats = [e for e in prenoms if e not in pris_ce_jour]
            
            # Priorité à ceux qui ont le moins travaillé (équité)
            candidats.sort(key=lambda e: nb_taches_par_jeune[e])
            assignes = candidats[:besoin]
            
            for e in assignes:
                pris_ce_jour.add(e)
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(tache)
                planning.append({"Jour": f"Jour {jour}", "Tâche": tache, "Jeune": e})

    # =====================
    # AFFICHAGE
    # =====================
    df = pd.DataFrame(planning)
    st.success("Planning généré !")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("📊 Équilibre des tâches")
    st.bar_chart(pd.Series(nb_taches_par_jeune))

    # Export CSV
    st.download_button("⬇️ Télécharger CSV", df.to_csv(index=False), "planning.csv", "text/csv")
