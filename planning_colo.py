import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning Colo", layout="centered")
st.title("📅 Générateur de Planning des Tâches en Colo")

# --- Saisie des prénoms ---
st.header("👧👦 Enfants")
prenoms_input = st.text_area("Entrez un prénom par ligne :", height=200)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

# --- Paramètres du planning ---
st.header("📅 Paramètres du planning")
nb_jours = st.number_input("Nombre de jours de la colo :", min_value=1, max_value=30, value=5)

taches_input = st.text_area(
    "Tâches à planifier (une par ligne) :",
    value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nPrépa repas\nPrépa goûter\nNettoyage matin\nNettoyage soir\nCourses"
)
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# --- Nombre de personnes par tâche ---
nb_personnes_par_tache = {}
st.subheader("👥 Nombre de personnes par tâche")

max_people = max
