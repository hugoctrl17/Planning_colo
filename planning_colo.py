import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning Colo", page_icon="📅", layout="centered")

st.title("📅 Générateur de Planning des Tâches en Colo")

# --- Paramètres de base ---
st.sidebar.header("🎯 Paramètres du planning")

jours = st.sidebar.selectbox("Durée du séjour", [4, 5, 7, 14])
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

# --- Saisie des enfants ---
st.subheader("👧
