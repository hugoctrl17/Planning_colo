import streamlit as st
import pandas as pd
import json
from openai import OpenAI
from PIL import Image
import base64
import io

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =====================
# CONFIG
# =====================
st.set_page_config(
    page_title="Planning des tâches",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("GÉNÉRATEUR DE PLANNING DES TACHES")
uploaded_file = st.file_uploader(
    "Charger une configuration",
    type=["json"]
)

config_chargee = {}

if uploaded_file:
    config_chargee = json.load(uploaded_file)
st.header("Importer la liste des jeunes")

uploaded_image = st.file_uploader(
    "Importer une photo",
    type=["jpg", "jpeg", "png"]
)

if uploaded_image:
    image = Image.open(uploaded_image)

    st.image(
        image,
        caption="Document importé",
        use_container_width=True
    )

    if st.button("Extraire les jeunes"):
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        image_base64 = base64.b64encode(
            buffer.getvalue()
        ).decode()

# =====================
# LISTE DES JEUNES
# =====================
st.header("Liste des jeunes")

default_prenoms = ""

if config_chargee:
    default_prenoms = "\n".join(
        config_chargee.get("prenoms", [])
    )

prenoms_input = st.text_area(
    "Un prénom par ligne",
    value=default_prenoms,
    height=200,
    placeholder="Emma\nLéo\nNoah"
)

prenoms = [
    p.strip()
    for p in prenoms_input.split("\n")
    if p.strip()
]

nb_enfants = len(prenoms)

# =====================
# PARAMÈTRES GÉNÉRAUX
# =====================
st.header("Paramètres colo")
nb_jours = st.number_input(
    "Nombre de jours",
    min_value=1,
    max_value=30,
    value=config_chargee.get("nb_jours", 14)
)

liste_jours = list(range(1, nb_jours + 1))

# =====================
# LISTE DES TÂCHES
# =====================
st.header("Liste des tâches")
taches_input = st.text_area(
    "Une tâche par ligne",
    value=(
        "NETTOYAGE GITE MATIN (4) \n"
        "PREPA PIQUE NIQUE (8)\n"
        "PREPA REPAS MIDI (4)\n"
        "NETTOYAGE GITE MIDI (2)\n"
        "VAISELLE MIDI (4)\n"
        "NETTOYAGE GITE GOUTER (2)\n"
        "PREPA REPAS SOIR (4)\n"
        "NETTOYAGE GITE SOIR (2)\n"
        "VAISSELLE SOIR (4)\n"
        "COURSE (6)"
    )
)
taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

# =====================
# ⚙️ PARAMÈTRES PAR TÂCHE
# =====================
st.header("⚙️ Paramètres des tâches")

nb_personnes = {}
jours_par_tache = {}

for tache in taches:
    st.subheader(tache)

    nb_personnes[tache] = st.number_input(
        "👥 Nombre de jeunes nécessaires",
        min_value=1,
        max_value=max(1, nb_enfants),
        value=1,
        key=f"nb_{tache}"
    )

    jours_par_tache[tache] = st.multiselect(
        "📅 Jours où la tâche est effectuée",
        options=liste_jours,
        default=liste_jours,
        key=f"jours_{tache}"
    )

    st.divider()
def peut_faire_tache(enfant, tache, historique_taches):
   ###
   ###  Empêche de faire la même tâche 3 fois de suite.
   ###  

    historique = historique_taches[enfant]

    if len(historique) < 2:
        return True

    return not (
        historique[-1] == tache
        and historique[-2] == tache
    )
def peut_faire_tache(enfant, tache, historique_taches):
    """
    Empêche de faire la même tâche 3 fois de suite.
    """

    historique = historique_taches[enfant]

    if len(historique) < 2:
        return True

    return not (
        historique[-1] == tache
        and historique[-2] == tache
    )
# =====================
# 🎲 GÉNÉRATION DU PLANNING
# =====================
config = {
    "nb_jours": nb_jours,
    "prenoms": prenoms,
    "taches": taches,
    "nb_personnes": nb_personnes,
    "jours_par_tache": jours_par_tache
}

json_data = json.dumps(
    config,
    ensure_ascii=False,
    indent=4
)

st.download_button(
    "💾 Sauvegarder la configuration",
    data=json_data,
    file_name="configuration_colo.json",
    mime="application/json",
    use_container_width=True
)
st.header("GÉNÉRER")
config = {
    "nb_jours": nb_jours,
    "prenoms": prenoms,
    "taches": taches,
    "nb_personnes": nb_personnes,
    "jours_par_tache": jours_par_tache
}
json_data = json.dumps(
    config,
    ensure_ascii=False,
    indent=4
)

st.download_button(
    "💾 Sauvegarder la configuration",
    data=json_data,
    file_name="configuration_colo.json",
    mime="application/json",
    use_container_width=True
)

if st.button("GÉNÉRER LE PLANNING", use_container_width=True):

    if not prenoms:
        st.error("❌ Ajoute au moins un jeune.")
        st.stop()

    if not taches:
        st.error("❌ Ajoute au moins une tâche.")
        st.stop()

    planning = []
    alertes = []

    # Historique
    taches_par_enfant = {e: set() for e in prenoms}
    nb_taches_enfant = {e: 0 for e in prenoms}
    historique_taches = {e: [] for e in prenoms}

    for jour in range(1, nb_jours + 1):
        pris_ce_jour = set()

        for tache in taches:

            # ❌ tâche non prévue ce jour-là
            if jour not in jours_par_tache.get(tache, []):
                continue

            besoin = min(nb_personnes[tache], nb_enfants)

            # Enfants disponibles + n'ayant jamais fait cette tâche
           eligibles = [
    e for e in prenoms
    if e not in pris_ce_jour
    and peut_faire_tache(e, tache, historique_taches)
]

            # Équilibrage : ceux qui ont le moins travaillé
            eligibles.sort(key=lambda e: nb_taches_enfant[e])

            # Fallback : autoriser un doublon si nécessaire
            if len(eligibles) < besoin:
                fallback = [
                    e for e in prenoms
                    if e not in pris_ce_jour and e not in eligibles
                ]
                fallback.sort(key=lambda e: nb_taches_enfant[e])
                eligibles += fallback

            assignes = eligibles[:besoin]

            if len(assignes) < besoin:
                alertes.append(
                    f"Jour {jour} – {tache} : {besoin - len(assignes)} place(s) manquante(s)"
                )

           for e in assignes:
    pris_ce_jour.add(e)

    taches_par_enfant[e].add(tache)
    nb_taches_enfant[e] += 1

    historique_taches[e].append(tache)

            planning.append({
                "Jour": f"Jour {jour}",
                "Tâche": tache,
                "Jeunes": ", ".join(assignes) if assignes else "—"
            })

    # =====================
    # 📊 AFFICHAGE
    # =====================
    df = pd.DataFrame(planning)
    st.success("✅ Planning généré")

    st.dataframe(df, use_container_width=True)

    # =====================
    # 📅 VUE PAR JOUR (MOBILE FRIENDLY)
    # =====================
    st.header("📅 Vue par jour")
    for jour in df["Jour"].unique():
        st.subheader(jour)
        jour_df = df[df["Jour"] == jour]
        for _, row in jour_df.iterrows():
            st.markdown(f"• **{row['Tâche']}** → {row['Jeunes']}")

    # =====================
    # 🚨 ALERTES
    # =====================
    if alertes:
        st.warning("⚠️ Alertes")
        for a in alertes:
            st.write("•", a)

    # =====================
    # 📊 RÉCAP PAR JEUNE
    # =====================
    st.header("📊 Récapitulatif par jeune")
    recap = pd.DataFrame([
        {
            "Jeune": e,
            "Nombre de tâches": nb_taches_enfant[e],
            "Tâches effectuées": ", ".join(historique_taches[e])    
        }
        for e in prenoms
    ])
    st.dataframe(recap, use_container_width=True)

    # =====================
    # ⬇️ EXPORT CSV
    # =====================
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Télécharger le planning (CSV)",
        data=csv,
        file_name="planning_taches_colo.csv",
        mime="text/csv",
        use_container_width=True
    )
