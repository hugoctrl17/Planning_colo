import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import numpy as np
import cv2
import io

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Planning Colo", layout="centered")
st.title("📱 Planning Colo - Version Stable")

# =====================
# SESSION STATE SAFE
# =====================
if "prenoms" not in st.session_state:
    st.session_state.prenoms = []

# =====================
# OCR GRATUIT
# =====================
def ocr_image(image):
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

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
# UPLOAD IMAGE + OCR
# =====================
st.header("📸 OCR (liste des jeunes)")

img_file = st.file_uploader("Importer une image", type=["png", "jpg", "jpeg"])

ocr_text = ""

if img_file:
    image = Image.open(img_file)
    st.image(image, use_container_width=True)

    if st.button("🔍 Extraire texte OCR"):
        raw = ocr_image(image)
        ocr_text = clean_text(raw)

        st.session_state.prenoms = ocr_text.split("\n")

# =====================
# INPUT PRÉNOMS
# =====================
st.header("👦 Jeunes")

prenoms_input = st.text_area(
    "Un prénom par ligne",
    value="\n".join(st.session_state.prenoms),
    height=180
)

st.session_state.prenoms = [
    p.strip() for p in prenoms_input.split("\n") if p.strip()
]

prenoms = st.session_state.prenoms

st.write(f"👥 {len(prenoms)} jeunes")

# =====================
# JOURS
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

# sécurité slider
max_people = len(prenoms) if len(prenoms) > 0 else 1

nb_personnes = {}
for t in taches:
    nb_personnes[t] = st.slider(
        f"{t} 👥",
        min_value=1,
        max_value=max_people,
        value=1,
        key=f"slider_{t}"
    )

# =====================
# ALGO ÉQUITÉ SIMPLE + STABLE
# =====================
def choisir(prenoms, besoin, stats, last_task, tache):
    scores = []

    for p in prenoms:
        score = stats[p] * 10

        if last_task[p] == tache:
            score += 50

        scores.append((score, p))

    scores.sort(key=lambda x: x[0])

    return [p for _, p in scores[:besoin]]

# =====================
# GÉNÉRATION
# =====================
if st.button("🚀 Générer planning", use_container_width=True):

    if len(prenoms) == 0:
        st.error("Ajoute au moins un jeune")
        st.stop()

    planning = []
    stats = {p: 0 for p in prenoms}
    last_task = {p: None for p in prenoms}

    for j in jours:

        st.subheader(f"📅 Jour {j}")

        used = set()

        for t in taches:

            candidats = [p for p in prenoms if p not in used]

            if not candidats:
                continue

            besoin = nb_personnes[t]

            assignes = choisir(
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
        {"Jeune": p, "Tâches": stats[p]}
        for p in prenoms
    ]).sort_values("Tâches")

    st.dataframe(recap, use_container_width=True)

    # =====================
    # EXPORT CSV
    # =====================
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇️ CSV",
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
        "📥 Excel",
        data=buffer.getvalue(),
        file_name="planning.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
