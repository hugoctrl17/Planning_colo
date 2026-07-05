import streamlit as st
import pandas as pd

st.title("📅 Générateur de Planning Colo")

# --- Inputs ---
prenoms_input = st.text_area("Prénoms (un par ligne)", "Emma\nLéo\nNoah\nJade\nLucas")
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_jours = st.number_input("Nombre de jours", 1, 30, 5)

taches_input = st.text_area("Tâches (format: Nom (nb_personnes))", "Vaisselle (2)\nNettoyage (2)\nCuisine (3)")
taches_config = []
for ligne in taches_input.split("\n"):
    if "(" in ligne:
        nom = ligne.split("(")[0].strip()
        nb_str = ligne.split("(")[1].replace(")", "").strip()
        if nb_str.isdigit():
            taches_config.append({"nom": nom, "nb": int(nb_str)})

if st.button("Générer le planning"):
    if not prenoms or not taches_config:
        st.error("Erreur : Remplis bien la liste des jeunes et des tâches.")
        st.stop()

    # Initialisation
    planning = []
    # On garde une trace de ce que chaque jeune a fait : {jeune: [taches_faites_au_total]}
    historique_taches = {p: [] for p in prenoms}

    for jour in range(1, nb_jours + 1):
        # Liste des jeunes disponibles ce jour-là (on réinitialise chaque jour)
        disponibles = list(prenoms)
        random.shuffle(disponibles) # Mélange pour ne pas toujours prendre les mêmes en premier
        
        for t in taches_config:
            besoin = t['nb']
            assignes = []
            
            # On cherche des candidats
            # Critère 1 : N'a pas fait la même tâche hier ou avant-hier
            candidats = []
            for p in disponibles:
                # Vérifie les 2 derniers jours dans l'historique
                dernieres_taches = historique_taches[p][-2:] 
                if t['nom'] not in dernieres_taches:
                    candidats.append(p)
            
            # Si on n'a pas assez de candidats "frais", on prend dans les disponibles restants
            if len(candidats) < besoin:
                candidats = disponibles
            
            # On sélectionne les premiers de la liste
            assignes = candidats[:besoin]
            
            # On met à jour les listes
            for p in assignes:
                disponibles.remove(p)
                historique_taches[p].append(t['nom'])
                planning.append({"Jour": jour, "Tâche": t['nom'], "Jeune": p})

    # --- AFFICHAGE ---
    df = pd.DataFrame(planning)
    st.success("Planning généré avec succès !")
    st.dataframe(df, use_container_width=True)

    # Récapitulatif
    st.subheader("📊 Récapitulatif par jeune")
    recap = df.groupby('Jeune')['Tâche'].count()
    st.bar_chart(recap)
