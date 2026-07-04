import streamlit as st
import pandas as pd
import json
from PIL import Image
import pytesseract
import numpy as np
import cv2
import io

# =====================
# CONFIG STREAMLIT
# =====================
st.set_page_config(page_title="Planning Colo", layout="centered")

st.title("📱 GÉNÉRATEUR DE PLANNING ÉQUITABLE")

# =====================
# OCR GRATUIT AMÉLIORÉ
# =====================
def ocr_image(image):
    img = np.array(image)

    # grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # amélioration contraste
    gray = cv2.equalizeHist(gray)

    # réduction bruit
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # binarisation
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # OCR
    config = "--psm 6"
    text = pytesseract.image_to_string(
        thresh,
        lang="fra+eng",
        config=config
    )

    return text


def clean_text(text):
    return "\n".join(
        [t.strip() for t in text.split("\n") if len(t.strip()) > 1]
    )

# =====================
# IMAGE + OCR
# =====================
st.header("📸 OCR (liste jeunes)")

img_file = st.file_uploader("Importer une image", type=["png", "jpg", "jpeg"])

ocr_text = ""

if img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

    if st.button("🔍 Extraire texte"):
        raw = ocr_image(image)
        ocr_text = clean_text(raw)
        st.text_area("Texte détecté", ocr_text, height=200)

# =====================
# JEUNES
# =====================
st.header("👦 Liste des jeunes")

default_text = ocr_text if ocr_text else ""

prenoms_input = st.text_area(
    "Un prénom par ligne",
    value=default_text,
    height=180
)

prenoms = [p.strip() for p in prenoms_input.split("\n") if p.strip()]

st.write(f"👥 {len(prenoms)} jeunes")

# =====================
# PARAMÈTRES
# =====================
nb_jours = st.slider("📅 Nombre de jours", 1, 30, 7)
jours = list(range(1, nb_jours + 1))

# =====================
# TÂCHES
# =====================
st.header("🧹 Tâches")

taches_input = st.text_area(
    "Une tâche par ligne",
    value="Cuisine\nVaisselle\nMénage\nCourses",
    height=120
)

taches = [t.strip() for t in taches_input.split("\n") if t.strip()]

nb_personnes = {
    t: st.slider(f"{t} 👥", 1, max(1, len(prenoms)), 1)
    for t in taches
}

# =====================
# ⚖️ ALGO D'ÉQUITÉ AVANCÉ
# =====================
def choisir_equitable(prenoms, besoin, stats, last_task, tache):
    """
    Score :
    - + poids si déjà beaucoup travaillé
    - + pénalité si même tâche récente
    """

    scores = []

    for p in prenoms:
        score = 0

        # équilibre global
        score += stats[p] * 10

        # éviter répétition tâche
        if last_task[p] == tache:
            score += 50

        scores.append((score, p))

    scores.sort(key=lambda x: x[0])

    return [p for _, p in scores[:besoin]]

# =====================
# GÉNÉRATION
# =====================
if st.button("🚀 Générer le planning", use_container_width=True):

    if not prenoms:
        st.error("Ajoute des jeunes")
        st.stop()

    planning = []
    stats = {p: 0 for p in prenoms}
    last_task = {p: None for p in prenoms}

    for j in jours:

        st.subheader(f"📅 Jour {j}")

        used = set()

        for t in taches:

            candidats = [
                p for p in prenoms
                if p not in used
            ]

            if not candidats:
                continue

            besoin = nb_personnes[t]

            assignes = choisir_equitable(
                candidats,
                besoin,
                stats,
                last_task,
                t
            )

            for a in assignes:
                stats[a] += 1
                last_task[a] = t
                used.add(a)

            st.write(f"🧹 **{t}** → {', '.join(assignes)}")

            planning.append({
                "Jour": j,
                "Tâche": t,
                "Jeunes": ", ".join(assignes)
            })

    df = pd.DataFrame(planning)

    st.success("✅ Planning généré")

    st.dataframe(df, use_container_width=True)

    # =====================
    # RÉCAP ÉQUITÉ
    # =====================
    st.header("📊 Équité")

    recap = pd.DataFrame([
        {
            "Jeune": p,
            "Tâches": stats[p]
        }
        for p in prenoms
    ]).sort_values("Tâches")

    st.dataframe(recap, use_container_width=True)

    # =====================
    # EXPORT CSV
    # =====================
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ Télécharger CSV",
        data=csv,
        file_name="planning.csv",
        mime="text/csv"
    )

    # =====================
    # EXPORT EXCEL
    # =====================
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="planning")

    st.download_button(
        "📥 Télécharger Excel",
        data=buffer.getvalue(),
        file_name="planning.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
