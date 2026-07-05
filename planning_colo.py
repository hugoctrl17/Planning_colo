import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Planning colo", layout="centered")

st.title("📅 Générateur de planning équitable")

# --- Inputs ---
prenoms_input = st.text_area("Prénoms des jeunes (un par ligne)", "Emma\nLéo\nNoah\nJade\nLucas")
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_jours = st.number_input("Nombre de jours", 1, 30, 5)

taches_input = st.text_area("Tâches (format: Nom (nb_personnes))", "Vaisselle (2)\nNettoyage (2)\nCuisine (3)")
taches_config = []
for ligne in taches_input.split("\n"):
    if "(" in ligne:
        nom = ligne.split("(")[0].strip()
        nb = int(ligne.split("(")[1].replace(")", "").strip())
        taches_config.append({"nom": nom, "nb": nb})

# --- Logique de génération ---
if st.button("Générer le planning"):
    # Historique : {nom: [liste des tâches faites par jour]}
    # Pour gérer le "pas 2 fois la même en 2-3 jours", on regarde l'historique récent
    historique = {p: [] for p in prenoms} 
    planning = []
    
    # On définit l'intervalle de repos (ex: 2 jours)
    repos_intervalle = 2 

    for jour in range(1, nb_jours + 1):
        pris_ce_jour = []
        
        for t in taches_config:
            # Qui est dispo ?
            # 1. Pas déjà pris aujourd'hui
            # 2. N'a pas fait cette tâche précise dans les 'repos_intervalle' derniers jours
            candidats = []
            for p in prenoms:
                if p not in pris_ce_jour:
                    # Vérifier si le jeune a fait cette tâche récemment
                    recent = historique[p][-repos_intervalle:]
                    if t['nom'] not in recent:
                        candidats.append(p)
            
            # Si pas assez de candidats, on relâche la contrainte de "tâche récente"
            if len(candidats) < t['nb']:
                candidats = [p for p in prenoms if p not in pris_ce_jour]
            
            # Priorité à celui qui a fait le moins de tâches au total
            candidats.sort(key=lambda p: len(historique[p]))
            
            assignes = candidats[:t['nb']]
            pris_ce_jour.extend(assignes)
            
            for p in assignes:
                historique[p].append(t['nom'])
                planning.append({"Jour": jour, "Tâche": t['nom'], "Jeune": p})

    # Affichage
    df = pd.DataFrame(planning)
    st.dataframe(df)
    
    # Graphique d'équité
    st.subheader("📊 Nombre de tâches par jeune")
    recap = df['Jeune'].value_counts()
    st.bar_chart(recap)
