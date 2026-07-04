import streamlit as st
import pandas as pd
from ortools.sat.python import cp_model

# =====================
# INPUTS
# =====================
st.title("PLANNING OPTIMISÉ (SOLVEUR)")

prenoms = [p.strip() for p in st.text_area("Jeunes", "Emma\nLéo\nNoah").split("\n") if p.strip()]
taches_input = st.text_area("Tâches (nom;besoin)", "Nettoyage;2\nVaisselle;2\nCuisine;3")

taches = []
for line in taches_input.split("\n"):
    if ";" in line:
        name, nb = line.split(";")
        taches.append((name.strip(), int(nb.strip())))

nb_jours = st.number_input("Jours", 1, 30, 3)

# =====================
# MODEL
# =====================
model = cp_model.CpModel()

# x[jour, tache, personne]
x = {}

for j in range(nb_jours):
    for t, besoin in taches:
        for p in prenoms:
            x[(j, t, p)] = model.NewBoolVar(f"x_{j}_{t}_{p}")

# =====================
# CONTRAINTES
# =====================

# 1. Chaque tâche doit être exactement remplie
for j in range(nb_jours):
    for t, besoin in taches:
        model.Add(
            sum(x[(j, t, p)] for p in prenoms) == besoin
        )

# 2. max 2 tâches par jour par personne
for j in range(nb_jours):
    for p in prenoms:
        model.Add(
            sum(x[(j, t, p)] for t, _ in taches) <= 2
        )

# 3. pas 2 fois même tâche pour une personne
for p in prenoms:
    for t, _ in taches:
        model.Add(
            sum(x[(j, t, p)] for j in range(nb_jours)) <= 1
        )

# =====================
# OBJECTIF : ÉQUILIBRE
# =====================
load = {p: model.NewIntVar(0, 100, f"load_{p}") for p in prenoms}

for p in prenoms:
    model.Add(
        load[p] ==
        sum(x[(j, t, p)] for j in range(nb_jours) for t, _ in taches)
    )

# minimiser différence entre charges
max_load = model.NewIntVar(0, 100, "max_load")
min_load = model.NewIntVar(0, 100, "min_load")

model.AddMaxEquality(max_load, list(load.values()))
model.AddMinEquality(min_load, list(load.values()))

model.Minimize(max_load - min_load)

# =====================
# SOLVE
# =====================
solver = cp_model.CpSolver()
status = solver.Solve(model)

# =====================
# RESULT
# =====================
if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:

    planning = []

    for j in range(nb_jours):
        for t, _ in taches:
            personnes = [
                p for p in prenoms
                if solver.Value(x[(j, t, p)]) == 1
            ]

            planning.append({
                "Jour": f"Jour {j+1}",
                "Tâche": t,
                "Jeunes": ", ".join(personnes)
            })

    df = pd.DataFrame(planning)

    st.success("Planning optimisé généré")

    st.dataframe(df, use_container_width=True)

    st.header("📊 Charge par personne")

    load_data = []
    for p in prenoms:
        load_data.append({
            "Jeune": p,
            "Tâches": sum(
                solver.Value(x[(j, t, p)])
                for j in range(nb_jours)
                for t, _ in taches
            )
        })

    st.dataframe(pd.DataFrame(load_data))

else:
    st.error("Aucune solution possible avec ces contraintes 😢")
