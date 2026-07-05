import streamlit as st
import pandas as pd
import json
import random

st.set_page_config(page_title="Planning Colo", layout="wide")
st.title("📅 Générateur de Planning Colo")

# ... (Configuration reste identique, saute à la génération) ...
# [Gardez les blocs de configuration précédents jusqu'au if st.button...]

if st.button("GÉNÉRER LE PLANNING", use_container_width=True):
    planning = []
    historique_taches = {e: [] for e in prenoms}
    nb_taches_par_jeune = {e: 0 for e in prenoms}

    for jour in liste_jours:
        pris_ce_jour = set()
        
        for nom_tache in taches: # Utilisation de la liste originale des tâches
            tache_nom = nom_tache.split('(')[0].strip()
            
            if jour not in jours_par_tache.get(tache_nom, []): 
                # On ajoute une entrée vide pour garder la structure du tableau
                planning.append({"Jour": jour, "Tâche": tache_nom, "Jeune": "-"})
                continue
            
            besoin = nb_personnes.get(tache_nom, 1)
            
            # Sélection
            candidats = [e for e in prenoms if e not in pris_ce_jour]
            candidats.sort(key=lambda e: (
                100 if (historique_taches[e] and historique_taches[e][-1] == tache_nom) else 0,
                nb_taches_par_jeune[e],
                random.random()
            ))
            
            assignes = candidats[:besoin]
            
            for e in assignes:
                pris_ce_jour.add(e)
                nb_taches_par_jeune[e] += 1
                historique_taches[e].append(tache_nom)
                planning.append({"Jour": jour, "Tâche": tache_nom, "Jeune": e})

    # RÉSULTATS
    df = pd.DataFrame(planning)
    
    # FORCER LE TRI NUMÉRIQUE DES JOURS
    df['Jour'] = df['Jour'].astype(int)
    
    pivot_df = df.pivot_table(
        index="Tâche", 
        columns="Jour", 
        values="Jeune", 
        aggfunc=lambda x: "<br>".join([str(i) for i in x if i != "-"]),
        fill_value="-"
    )
    
    # Réordonner les colonnes (Jours)
    pivot_df = pivot_df.reindex(sorted(pivot_df.columns), axis=1)
    
    st.write(pivot_df.to_html(escape=False), unsafe_allow_html=True)
