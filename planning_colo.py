import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning Colo Pro", layout="centered")
st.title("📅 Générateur de Planning de Colo – Version Pro")

# =====================
# 👧👦 ENFANTS
# =====================
st.header("👧👦 Enfants")
prenoms_input = st.text_area("Un prénom par ligne :", height=200)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

# =====================
# 📅 PARAMÈTRES
# =====================
st.header("📅 Paramètres")
nb_jours = st.number_input("Nombre de jours", 1, 30, 5)

# =====================
# 🧹 TÂCHES
# =====================
st.header("🧹 Tâches")
taches_input = st.text_area(
    "Une tâche par ligne",
    value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nNettoyage matin\nNettoyage soir\nCourses"
)
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# =====================
# ⚙️ PARAMÈTRES DES TÂCHES
# =====================
st.subheader("⚙️ Paramètres par tâche")

nb_personnes = {}
penibilite = {}

for t in taches:
    col1, col2 = st.columns(2)
    with col1:
        nb_personnes[t] = st.number_input(
            f"{t} – personnes",
            1, max(1, nb_enfants), 1, key=f"p_{t}"
        )
    with col2:
        penibilite[t] = st.selectbox(
            f"{t} – pénibilité",
            [1, 2, 3],
            index=1,
            key=f"pen_{t}"
        )

# =====================
# 🚫 EXCLUSIONS
# =====================
st.header("🚫 Exclusions")
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
st.header("🧑‍🤝‍🧑 Binômes fixes (optionnel)")
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
# 🎲 GÉNÉRATION
# =====================
if st.button("🎲 Générer le planning"):
    if not prenoms or not taches:
        st.error("❌ Prénoms et tâches obligatoires")
        st.stop()

    planning = []
    alertes = []

    taches_par_enfant
