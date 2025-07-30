import streamlit as st
import random

st.set_page_config(page_title="Planning Colo", page_icon="📅", layout="centered")
st.title("📅 Générateur de Planning des Tâches en Colo")

# --- Saisie des enfants ---
st.subheader("👧👦 Enfants")
noms = st.text_area("Entrez un prénom par ligne :").strip().split("\n")
enfants = [nom.strip() for nom in noms if nom.strip()]
nb_enfants_total = len(enfants)

if nb_enfants_total == 0:
    st.warning("⚠️ Ajoute au moins un prénom pour continuer.")
    st.stop()

# --- Paramètres de durée ---
st.subheader("🗓️ Durée")
nb_jours = st.slider("Nombre de jours dans le planning :", min_value=1, max_value=30, value=7)

# --- Configuration des tâches dynamiques ---
st.subheader("🛠️ Tâches")
nb_taches = st.number_input("Combien de types de tâches veux-tu ?", min_value=1, max_value=20, value=5, step=1)

taches = {}
for i in range(nb_taches):
    col1, col2 = st.columns([3, 1])
    with col1:
        nom_tache = st.text_input(f"Tâche #{i+1}", value=f"Tâche {i+1}", key=f"tache_{i}")
    with col2:
        nb = st.number_input(f"Nb pers.", min_value=1, max_value=nb_enfants_total, value=2, step=1, key=f"nb_{i}")
    taches[nom_tache] = nb

# --- Génération du planning ---
if st.button("🎲 Générer le planning"):
    planning = {}
    historique = {e: set() for e in enfants}

    for jour in range(1, nb_jours + 1):
        planning[jour] = {}
        random.shuffle(enfants)

        for tache, nb in taches.items():
            choisis = []
            essais = 0
            while len(choisis) < nb and essais < 100:
                candidat = random.choice(enfants
