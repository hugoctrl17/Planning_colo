import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Planning Colo", layout="wide")
st.title("🗓️ Générateur de Planning des Tâches en Colo")

st.sidebar.header("Paramètres du Planning")
noms_text = st.sidebar.text_area("Liste des prénoms des enfants (un par ligne)", height=150)
enfants = [n.strip() for n in noms_text.split("\n") if n.strip()]
duree = st.sidebar.selectbox("Durée du planning (en jours)", options=[4, 5, 7, 14], index=2)

taches_default = {
    "Vaisselle matin": 2, "Vaisselle midi": 2, "Vaisselle soir": 2,
    "Prépa repas midi": 1, "Prépa repas soir": 1, "Prépa goûter": 1,
    "Nettoyage locaux matin": 2, "Nettoyage locaux midi": 2, "Nettoyage locaux soir": 2,
    "Courses": 2
}

st.sidebar.header("Configuration des tâches")
taches = {}
for tache, default_nb in taches_default.items():
    new_name = st.sidebar.text_input(f"Nom tâche (actuel: {tache})", value=tache, key=f"name_{tache}")
    max_enfants = max(1, len(enfants))  # on évite que max_value soit à 0
nb_enfants = st.sidebar.number_input(
    f"Nombre d'enfants pour '{new_name}'",
    min_value=1,
    max_value=max_enfants,
    value=min(default_nb, max_enfants),
    step=1,
    key=f"nb_{tache}"
)

if st.sidebar.button("Générer le planning"):
    if len(enfants) == 0:
        st.error("Merci d’entrer au moins un prénom d’enfant.")
    else:
        planning = []
        compteur_taches = {e: {t: 0 for t in taches} for e in enfants}
        np.random.seed()

        for jour in range(1, duree + 1):
            jour_taches = {"Jour": jour}
            for tache, nb in taches.items():
                enfants_tries = sorted(enfants, key=lambda e: compteur_taches[e][tache])
                selection = enfants_tries[:nb]
                for e in selection:
                    compteur_taches[e][tache] += 1
                jour_taches[tache] = ", ".join(selection)
            planning.append(jour_taches)

        df = pd.DataFrame(planning)
        st.write("### Planning généré :")
        st.dataframe(df, use_container_width=True)

        if st.button("🔁 Régénérer le planning"):
            st.experimental_rerun()
