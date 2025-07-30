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

# --- Saisie des tâches ---
taches_input = st.text_area(
    "Tâches à planifier (une par ligne) :",
    value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nPrépa repas\nPrépa goûter\nNettoyage matin\nNettoyage soir\nCourses"
)
# ✅ Correction de la ligne qui plantait
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# --- Nombre de personnes par tâche ---
st.subheader("👥 Nombre de personnes par tâche")
nb_personnes_par_tache = {}
max_people = max(1, nb_enfants)
for tache in taches:
    default_value = 1 if nb_enfants == 0 else min(2, max_people)
    nb = st.number_input(
        f"{tache}",
        min_value=1,
        max_value=max_people,
        value=default_value,
        key=f"nb_{tache}"
    )
    nb_personnes_par_tache[tache] = nb

# --- Bouton de génération (toujours visible) ---
generate = st.button("🎲 Générer le planning")

if generate:
    if nb_enfants == 0:
        st.error("❌ Ajoute au moins un prénom avant de générer.")
    elif len(taches) == 0:
        st.error("❌ Ajoute au moins une tâche.")
    else:
        planning = []
        for jour in range(1, nb_jours + 1):
            enfants_dispo = prenoms.copy()
            random.shuffle(enfants_dispo)
            for tache in taches:
                n = nb_personnes_par_tache[tache]
                n = min(n, len(prenoms))  # ✅ Empêche d'avoir plus de places que d'enfants
                if len(enfants_dispo) < n:
                    enfants_dispo = prenoms.copy()
                    random.shuffle(enfants_dispo)
                assignes = enfants_dispo[:n]
                enfants_dispo = enfants_dispo[n:]
                planning.append({
                    "Jour": f"Jour {jour}",
                    "Tâche": tache,
                    "Enfants": ", ".join(assignes)
                })

        df = pd.DataFrame(planning)
        st.success("✅ Planning généré avec succès !")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Télécharger en CSV", data=csv, file_name="planning_colo.csv", mime="text/csv")
