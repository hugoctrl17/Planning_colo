import streamlit as st
import pandas as pd
import json
from PIL import Image

# =====================
# CONFIG APP
# =====================
st.set_page_config(page_title="Planning", layout="centered")

st.title("GÉNÉRATEUR DE PLANNING")

# =====================
# IMPORT CONFIG
# =====================
file = st.file_uploader("Charger config JSON", type=["json"])

config = {}
if file:
    config = json.load(file)

# =====================
# JEUNES
# =====================
st.header("Jeunes")

default = "\n".join(config.get("prenoms", []))

prenoms_input = st.text_area("Un prénom par ligne", value=default, height=180)
prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]

# =====================
# GROUPES
# =====================
st.header("Groupes (optionnel)")

groupes_input = st.text_area(
    "Format: GR1: A, B, C",
    value=""
)

groupes = {}
for line in groupes_input.split("\n"):
    if ":" in line:
        g, members = line.split(":")
        groupes[g.strip()] = [m.strip() for m in members.split(",") if m.strip()]

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
    "Une tâche par ligne (ex: NOM (4) GR1 / ALL)",
    value=(
        "NETTOYAGE MATIN (4) ALL\n"
        "PREPA REPAS (6) ALL\n"
        "VAISSELLE (4) ALL\n"
        "COURSE (3) ALL"
    )
)

# =====================
# PARSING TACHES
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
# PARAMS TACHES
# =====================
nb_personnes = {}
jours_par_tache = {}

st.header("Répartition tâches")

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
# SCORE EQUITE
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
        pris = set()
        jour_vide = True

        for name, grp in taches:

            if jour not in jours_par_tache[name]:
                continue

            besoin = min(nb_personnes[name], len(prenoms))

            # =====================
            # CANDIDATS
            # =====================
            if grp == "ALL":
                candidats = prenoms
            else:
                candidats = groupes.get(grp, prenoms)

            candidats = [
                e for e in candidats
                if jour_compteur[e] < 2
                and name not in taches_faites[e]
                and e not in pris
            ]

            candidats.sort(key=score)

            assignes = candidats[:besoin]

            # =====================
            # Fallback automatique
            # =====================
            if len(assignes) < besoin:
                fallback = [
                    e for e in prenoms
                    if jour_compteur[e] < 2
                    and name not in taches_faites[e]
                    and e not in assignes
                ]
                fallback.sort(key=score)
                assignes += fallback[:besoin - len(assignes)]

            # =====================
            # SI TOUJOURS VIDE → FORCAGE
            # =====================
            if not assignes and prenoms:
                assignes = [min(prenoms, key=lambda x: nb_taches[x])]

            if assignes:
                jour_vide = False

            for e in assignes:
                pris.add(e)
                taches_faites[e].add(name)
                nb_taches[e] += 1
                jour_compteur[e] += 1

            planning.append({
                "Jour": f"Jour {jour}",
                "Tâche": name,
                "Groupe": grp,
                "Jeunes": ", ".join(assignes) if assignes else "—"
            })

        # =====================
        # SI JOUR VIDE → REMPLISSAGE GLOBAL
        # =====================
        if jour_vide:
            fallback_task = {
                "Jour": f"Jour {jour}",
                "Tâche": "🔧 AIDE GÉNÉRALE",
                "Groupe": "ALL",
                "Jeunes": ", ".join(sorted(prenoms, key=lambda x: nb_taches[x])[:2])
            }
            planning.append(fallback_task)

    # =====================
    # RESULTAT
    # =====================
    df = pd.DataFrame(planning)

    st.success("Planning généré sans jours vides")

    st.dataframe(df, use_container_width=True)

    # =====================
    # VUE PAR JOUR
    # =====================
    st.header("📅 Vue par jour")

    for j in df["Jour"].unique():
        st.subheader(j)
        for _, r in df[df["Jour"] == j].iterrows():
            st.write(f"{r['Tâche']} → {r['Jeunes']}")

    # =====================
    # RECAP
    # =====================
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

    # =====================
    # EXPORT
    # =====================
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Export CSV",
        data=csv,
        file_name="planning.csv",
        mime="text/csv"
    )
