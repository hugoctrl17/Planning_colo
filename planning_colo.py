import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="PLANNING TACHES ", layout="centered")
st.title("GENERATEUR DE PLANNING DES TACHES")

# =====================
# 👧👦 ENFANTS
# =====================
st.header("LISTE DES JEUNES")
prenoms_input = st.text_area("Un prénom par ligne :", height=200)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

# =====================
# 📅 PARAMÈTRES
# =====================
st.header("NOMBRE DE JOURS DE LA COLO")
nb_jours = st.number_input("Nombre de jours", 1, 30, 5)

# =====================
# 🧹 TÂCHES
# =====================
st.header("LISTE DES TACHES")
taches_input = st.text_area(
    "Une tâche par ligne",
    value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nNettoyage matin\nNettoyage soir\nCourses"
)
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# =====================
# ⚙️ PARAMÈTRES DES TÂCHES
# =====================
st.subheader("JEUNES PAR TACHE")

nb_personnes = {}
penibilite = {}

for t in taches:
    col1, col2 = st.columns(2)
    with col1:
        nb_personnes[t] = st.number_input(
            f"{t} – personnes",
            1, max(1, nb_enfants), 1, key=f"p_{t}"
        )
   

# =====================
# 🚫 EXCLUSIONS
# =====================
st.header("EXCLUSIONS")
exclusions = {}
for e in prenoms:
    exclusions[e] = st.multiselect(
        f"{e} ne peut PAS faire :",
        taches,
        key=f"excl_{e}"
    )

# =====================
# 🧑‍🤝‍🧑 BINÔMES
# =====================
st.header("BINÔMES (optionnel)")
binomes_input = st.text_area(
    "Un binôme par ligne (ex : Paul,Marie)",
    height=100
)
binomes = []
for line in binomes_input.split("\n"):
    parts = [p.strip() for p in line.split(",")]
    if len(parts) == 2 and all(p in prenoms for p in parts):
        binomes.append(tuple(parts))

# =====================
# GÉNÉRATION
# =====================
if st.button("GENERER LE PLANNING"):
    if not prenoms or not taches:
        st.error("❌ Prénoms et tâches obligatoires")
        st.stop()

    planning = []
    alertes = []

    taches_par_enfant
