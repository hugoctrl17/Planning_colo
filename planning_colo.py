import streamlit as st
import pandas as pd
import json
from PIL import Image

# =====================
# CONFIG APP
# =====================
st.set_page_config(
    page_title="Planning des tâches",
    layout="centered"
)

st.title("GÉNÉRATEUR DE PLANNING")

# =====================
# CONFIG IMPORT
# =====================
uploaded_file = st.file_uploader("Charger config JSON", type=["json"])

config = {}
if uploaded_file:
    config = json.load(uploaded_file)

# =====================
# JEUNES + GROUPES
# =====================
st.header("Jeunes")

default = "\n".join(config.get("prenoms", []))

prenoms_input = st.text_area("Un prénom par ligne", value=default, height=180)

prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]

# GROUPES (NOUVEAU)
st.header("Groupes (optionnel)")

groupes_input = st.text_area(
    "Un groupe par ligne ",
    value="GR1: " + ", ".join(prenoms[:len(prenoms)//2]) if prenoms else ""
)

groupes = {}
for line in groupes_input.split("\n"):
    if ":" in line:
        nom, membres = line.split(":")
        groupes[nom.strip()] = [m.strip() for m in membres.split(",") if m.strip()]

# =====================
# PARAMÈTRES
# =====================
st.header("Paramètres")

nb_jours = st.number_input("Nombre de jours", 1, 30, 7)
jours = list(range(1, nb_jours + 1))

# =====================
# TÂCHES
# =====================
st.header("Tâches")

taches_input = st.text_area(
    "Une tâche par ligne",
    value=(
        "NETTOYAGE (4) \n"
        "PREPA REPAS (6) \n"
        "VAISSELLE (4) \n"
        "COURSE (3) "
    )
)

# =====================
# PARSE TACHES
# =====================
taches = []
for line in taches_input.split("\n"):
    line = line.strip()
    if not line:
        continue

    parts = line.split()

    groupe = "ALL"
    if parts[-1].startswith("GR"):
        groupe = parts[-1]
        name = " ".join(parts[:-1])
    else:
        name = line

    taches.append((name, groupe))

# =====================
# PARAMÈTRES TACHES
# =====================
st.header("Répartition")

nb_personnes = {}
jours_par_tache = {}

for name, grp in taches:
    st.subheader(name)

    nb_personnes[name] = st.number_input(
        f"👥 {name}",
        1,
        max(1, len(prenoms)),
        1,
        key=f"nb_{name}"
    )

    jours_par_tache[name] = st.multiselect(
        f"📅 jours {name}",
        jours,
        default=jours,
        key=f"jours_{name}"
    )

# =====================
# LOGIQUE
# =====================

def score(e):
    return (
        nb_taches[e],
        len(taches_faites[e])
    )

# =====================
# GENERATION
# =====================
if st.button("GÉNÉRER"):

    if not prenoms:
        st.error("Ajoute des jeunes")
        st.stop()

    planning = []

    taches_faites = {e: set() for e in prenoms}
    nb_taches = {e: 0 for e in prenoms}
    jour_compteur = {e: 0 for e in prenoms}

    for jour in jours:
        deja_pris = set()

        for name, grp in taches:

            if jour not in jours_par_tache[name]:
                continue

            besoin = min(nb_personnes[name], len(prenoms))

            # =====================
            # groupe filtering
            # =====================
            if grp == "ALL":
                candidats = prenoms
            else:
                candidats = groupes.get(grp, prenoms)

            # limite 2 tâches / jour
            candidats = [
                e for e in candidats
                if jour_compteur[e] < 2
                and name not in taches_faites[e]
                and e not in deja_pris
            ]

            candidats.sort(key=score)

            assignes = candidats[:besoin]

            # =====================
            # COMPLETION AUTOMATIQUE
            # =====================
            if len(assignes) < besoin:
                fallback = [
                    e for e in prenoms
                    if e not in assignes
                    and jour_compteur[e] < 2
                ]
                fallback.sort(key=score)
                assignes += fallback[:besoin - len(assignes)]

            for e in assignes:
                deja_pris.add(e)
                taches_faites[e].add(name)
                nb_taches[e] += 1
                jour_compteur[e] += 1

            planning.append({
                "Jour": f"Jour {jour}",
                "Tâche": name,
                "Groupe": grp,
                "Jeunes": ", ".join(assignes)
            })

    # =====================
    # RESULTAT
    # =====================
    df = pd.DataFrame(planning)

    st.success("Planning généré")

    st.dataframe(df, use_container_width=True)

    # vue par jour
    st.header("📅 Vue jour")
    for j in df["Jour"].unique():
        st.subheader(j)
        for _, r in df[df["Jour"] == j].iterrows():
            st.write(f"{r['Tâche']} ({r['Groupe']}) → {r['Jeunes']}")

    # recap
    st.header("📊 Récap")

    recap = pd.DataFrame([
        {
            "Jeune": e,
            "Tâches": nb_taches[e],
            "Jours occupés": jour_compteur[e]
        }
        for e in prenoms
    ])

    st.dataframe(recap, use_container_width=True)

    # export
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Export CSV",
        data=csv,
        file_name="planning.csv",
        mime="text/csv"
    )
