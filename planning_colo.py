import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning Colo", page_icon="📅", layout="centered")
st.title("📅 Générateur de Planning des Tâches en Colo")

# --- Liste des enfants ---
st.subheader("👧👦 Liste des enfants")
noms = st.text_area("Entrez un prénom par ligne :").strip().split("\n")
enfants = [nom.strip() for nom in noms if nom.strip()]
nb_enfants_total = len(enfants)

if nb_enfants_total == 0:
    st.warning("⚠️ Ajoutez au moins un prénom pour continuer.")
    st.stop()

# --- Paramètres de base ---
st.sidebar.header("🎯 Paramètres du planning")
jours = st.sidebar.selectbox("Durée du séjour (en jours)", [4, 5, 7, 14])

# --- Tâches paramétrables ---
st.subheader("🧹 Configuration des tâches")
taches_par_defaut = {
    "Vaisselle matin": 2,
    "Vaisselle midi": 2,
    "Vaisselle soir": 2,
    "Prépa repas midi": 2,
    "Prépa repas soir": 2,
    "Prépa goûter": 2,
    "Nettoyage matin": 2,
    "Nettoyage midi": 2,
    "Nettoyage soir": 2,
    "Courses": 2,
}

taches = {}
for tache, default_nb in taches_par_defaut.items():
    new_name = st.sidebar.text_input(f"Nom de tâche :", value=tache, key=f"label_{tache}")
    nb_max = max(1, nb_enfants_total)
    nb = st.sidebar.number_input(f"{new_name} - Nombre d'enfants", 1, nb_max, min(default_nb, nb_max), step=1, key=f"nb_{tache}")
    taches[new_name] = nb

# --- Génération du planning ---
if st.button("🎲 Générer le planning"):
    planning = {}
    historique = {e: set() for e in enfants}

    for jour in range(1, jours + 1):
        planning[jour] = {}
        disponibles = enfants[:]
        random.shuffle(disponibles)

        for tache, nb in taches.items():
            choisis = []
            essais = 0
            while len(choisis) < nb and essais < 100:
                candidat = random.choice(enfants)
                if candidat not in choisis and tache not in historique[candidat]:
                    choisis.append(candidat)
                    historique[candidat].add(tache)
                essais += 1
            planning[jour][tache] = choisis

    # --- Affichage du planning ---
    st.success("✅ Planning généré avec succès !")
    for jour in planning:
        st.subheader(f"📆 Jour {jour}")
        for tache, enfants_tache in planning[jour].items():
            st.markdown(f"🔸 **{tache}** : {', '.join(enfants_tache)}")
else:
    st.info("Clique sur le bouton pour générer un planning.")
