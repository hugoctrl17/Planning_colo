import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning Colo", layout="centered")

st.title("📅 Générateur de Planning des Tâches en Colo")

# --- Entrée des enfants ---
st.header("👦👧 Liste des enfants")
prenoms_input = st.text_area("Entrez un prénom par ligne :", height=200)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

# --- Paramètres du planning ---
st.header("🛠️ Paramètres du planning")
nb_jours = st.number_input("Nombre de jours de la colo :", min_value=1, max_value=30, value=7)

taches_input = st.text_area("Entrez les tâches (une par ligne) :", 
                            value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nPrépa repas midi
