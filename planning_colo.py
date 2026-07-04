import streamlit as st
import pandas as pd
import json
from PIL import Image

# =====================
# CONFIG APP
# =====================
st.set_page_config(
    page_title="Planning des tâches",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("GÉNÉRATEUR DE PLANNING DES TÂCHES")

# =====================
# IMPORT CONFIG
# =====================
uploaded_file = st.file_uploader(
    "Charger une configuration",
    type=["json"]
)

config_chargee = {}
if uploaded_file:
    config_chargee = json.load(uploaded_file)

# =====================
# IMAGE (option OCR future)
# =====================
st.header("Importer une photo")

uploaded_image = st.file_uploader(
    "Importer une image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="Document importé", use_container_width=True)

    st.info("OCR non activé (saisie manuelle actuellement).")

# =====================
# JEUNES
# =====================
st.header("Liste des jeunes")

default_prenoms = "\n".join(config_chargee.get("prenoms", []))

prenoms_input = st.text_area(
    "Un prénom par ligne",
    value=default_prenoms,
    height=200
)

prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]
nb_enfants = len(prenoms)

# =====================
# PARAMÈTRES
# =====================
st.header("Paramètres")

nb_jours = st.number_input(
    "Nombre de jours",
    min_value=1,
    max_value=30,
    value=config_chargee.get("nb_jours", 14)
)

jours = list(range(1, nb_jours + 1))

# =====================
# TÂCHES
# =====================
st.header("Tâches")

taches_input = st.text_area(
    "Une tâche par ligne",
    value=(
        "NETTOYAGE MATIN (4)\n"
        "PREPA PIQUE NIQUE (8)\n"
        "PREPA MIDI (4)\n"
        "VAISSELLE MIDI (4)\n"
        "NETTOYAGE SOIR (2)\n"
        "VAISSELLE SOIR (4)\n"
        "COURSE (6)"
    )
)

taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# =====================
# PARAMÈTRES PAR TÂCHE
# =====================
st.header("⚙️ Paramètres tâches")

nb_personnes = {}
jours_par_tache = {}

for t in taches:
    st.subheader(t)

    nb_personnes[t] = st.number_input(
        f"👥 {t} - nombre de personnes",
        min_value=1,
        max_value=max(1, nb_enfants),
        value=1,
        key=f"nb_{t}"
    )

    jours_par_tache[t] = st.multiselect(
        f"📅 Jours pour {t}",
        options=jours,
        default=jours,
        key=f"jours_{t}"
    )

    st.divider()

# =====================
# LOGIQUE ÉQUITÉ
# =====================

def peut_faire_tache(enfant, tache, historique):
    """Empêche 3 répétitions consécutives"""
    h = historique[enfant]
    if len(h) < 2:
        return True
    return not (h[-1] == tache and h[-2] == tache)


def score_equite(enfant):
    """Score global d'équité"""
    return (
        nb_taches_enfant[enfant],          # charge totale
        len(taches_par_enfant[enfant])     # diversité
    )

# =====================
# GÉNÉRATION
# =====================
if st.button("GÉNÉRER LE PLANNING", use_container_width=True):

    if not prenoms:
        st.error("Ajoute au moins un jeune.")
        st.stop()

    if not taches:
        st.error("Ajoute au moins une tâche.")
        st.stop()

    planning = []
    alertes = []

    taches_par_enfant = {e: set() for e in prenoms}
    nb_taches_enfant = {e: 0 for e in prenoms}
    historique_taches = {e: [] for e in prenoms}

    for jour in jours:
        pris = set()

        for tache in taches:

            if jour not in jours_par_tache.get(tache, []):
                continue

            besoin = min(nb_personnes[tache], nb_enfants)

            # =====================
            # ÉLIGIBLES (équité + interdiction répétition)
            # =====================
            eligibles = [
                e for e in prenoms
                if e not in pris
                and tache not in taches_par_enfant[e]  # ❌ jamais 2 fois même tâche
                and peut_faire_tache(e, tache, historique_taches)
            ]

            eligibles.sort(key=score_equite)

            assignes = eligibles[:besoin]

            # fallback si manque de monde
            if len(assignes) < besoin:
                fallback = [
                    e for e in prenoms
                    if e not in pris and e not in assignes
                ]
                fallback.sort(key=score_equite)
                assignes += fallback[:besoin - len(assignes)]

            if len(assignes) < besoin:
                alertes.append(f"Jour {jour} - {tache} : manque de personnes")

            for e in assignes:
                pris.add(e)
                taches_par_enfant[e].add(tache)
                nb_taches_enfant[e] += 1
                historique_taches[e].append(tache)

            planning.append({
                "Jour": f"Jour {jour}",
                "Tâche": tache,
                "Jeunes": ", ".join(assignes)
            })

    # =====================
    # RESULTATS
    # =====================
    df = pd.DataFrame(planning)

    st.success("Planning généré")

    st.dataframe(df, use_container_width=True)

    # Vue par jour
    st.header("📅 Vue par jour")
    for j in df["Jour"].unique():
        st.subheader(j)
        for _, row in df[df["Jour"] == j].iterrows():
            st.write(f"• {row['Tâche']} → {row['Jeunes']}")

    # alertes
    if alertes:
        st.warning("⚠️ Alertes")
        for a in alertes:
            st.write("•", a)

    # recap
    st.header("📊 Récap")

    recap = pd.DataFrame([
        {
            "Jeune": e,
            "Tâches": nb_taches_enfant[e],
            "Liste": ", ".join(historique_taches[e])
        }
        for e in prenoms
    ])

    st.dataframe(recap, use_container_width=True)

    # export CSV
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Télécharger CSV",
        data=csv,
        file_name="planning.csv",
        mime="text/csv"
    )
