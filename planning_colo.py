import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="Planning Colo", layout="centered")

st.title("📅 Générateur de Planning des Tâches en Colo")

# Saisie des prénoms
st.markdown("## 👧👦 Entrez les prénoms des enfants")
prenoms_input = st.text_area("Entrez un prénom par ligne :", height=200)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants_total = len(prenoms)

# Configuration des tâches
st.markdown("## 🧹 Configuration des tâches")
jours = st.number_input("Nombre de jours de colo", min_value=1, max_value=30, value=7)

taches = st.text_area("Entrez les tâches (une par ligne) :", 
                      value="Vaisselle midi\nVaisselle soir\nPrépa repas\nPrépa goûter\nNettoyage matin\nCourses")
liste_taches = [t.strip() for t in taches.split("\n") if t.strip()]

nb_par_tache = {}
for i, t in enumerate(liste_taches):
    nb = st.number_input(
        f"Nb pers. pour « {t} »", 
        min_value=1, 
        max_value=nb_enfants_total if nb_enfants_total > 0 else 1)
