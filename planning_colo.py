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

taches_input = st.text_area("Tâches à planifier (une par ligne) :", 
                            value="Vaisselle matin\nVaisselle midi\nVaisselle soir\nPrépa repas\nPrépa goûter\nNettoyage matin\nNettoyage soir\nCourses")
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

nb_personnes_par_tache = {}
st.subheader("👥 Nombre de personnes par tâche")
for tache in taches:
    nb = st.number_input(f"{tache}", min_value=1, max_value=max(1, nb_enfants), value=2, key=tache)
    nb_personnes_par_tache[tache] = nb

# --- Bouton de génération ---
generate = st.button("🎲 Générer le planning")

if generate:
    if nb_enfants == 0 or len(taches) == 0:
        st.error("Veuillez entrer au moins un prénom et une tâche.")
    else:
        planning = []
        for jour in range(1, nb_jours + 1):
            enfants_dispo = prenoms.copy()
            random.shuffle(enfants_dispo)
            ligne_jour = []
            for tache in taches:
                n = nb_personnes_par_tache[tache]
                if len(enfants_dispo) < n:
                    enfants_dispo = prenoms.copy()
                    random.shuffle(enfants_dispo)
                assignés = enfants_dispo[:n]
                enfants_dispo = enfants_dispo[n:]
                ligne_jour.append({
                    "Jour": f"Jour {jour}",
                    "Tâche": tache,
                    "Enfants": ", ".join(assignés)
                })
            planning.extend(ligne_jour)

        df = pd.DataFrame(planning)
        st.success("✅ Planning généré avec succès !")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Télécharger en CSV", data=csv, file_name="planning_colo.csv", mime="text/csv")
