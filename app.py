# Murder Mystery AI Agent - fuld AI-drevet spilpakke med print, plot, GM og stemmer

import streamlit as st
import random
from typing import List, Dict
import base64
from fpdf import FPDF
import requests
import openai
import json

st.set_page_config(page_title="Murder Mystery AI", layout="centered")

# === Init session state ===
if "clues" not in st.session_state:
    st.session_state.clues = []
if "votes" not in st.session_state:
    st.session_state.votes = {}

# === Styling ===
st.markdown("""
    <style>
    .room-card {
        background-color: #eef1f5;
        padding: 10px;
        border-radius: 6px;
        margin: 6px 0;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .char-card {
        background-color: #fcfcfc;
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #999;
    }
    </style>
""", unsafe_allow_html=True)

# === AI-drevet plotgenerator ===
def generate_game():
    openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not openai.api_key:
        st.warning("API-nøgle mangler - kan ikke generere nyt AI-plot.")
        return {}

    prompt = (
        "Generer et komplet murder mystery plot til et brætspil. Inkluder: titel, tema, årstid, lokationstype, 6 karakterer med navn, rolle, hemmelighed og mål, en udpeget morder med motiv. Output i JSON-format."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        plot_data = json.loads(response.choices[0].message.content)
        return plot_data
    except Exception as e:
        st.error("Kunne ikke fortolke AI-plot som JSON.")
        return {}

game = generate_game()
st.subheader("🧬 Debug: AI-data")
st.json(game)

# === Vis plottet ===
if game:
    st.title(f"🎭 {game.get('titel', 'Murder Mystery')}")
    st.markdown(f"**Tema:** {game.get('tema')}  |  **Årstid:** {game.get('årstid')}  |  **Lokation:** {game.get('lokationstype')}")

    st.subheader("🎭 Karakterer")
    for char in game.get("karakterer", []):
        st.markdown(f"""
        <div class='char-card'>
        <b>{char['navn']}</b> – {char['rolle']}<br>
        🕵️ Hemmelighed: <i>{char['hemmelighed']}</i><br>
        🎯 Mål: {char['mål']}
        </div>
        """, unsafe_allow_html=True)

# === Sporlog ===
st.subheader("🔎 Sporlog")
new_clue = st.text_input("Tilføj et spor (observeret af spillerne eller Thorup):")
if st.button("➕ Tilføj spor") and new_clue:
    st.session_state.clues.append(new_clue)
    st.success("Spor tilføjet!")

if st.session_state.clues:
    for i, clue in enumerate(st.session_state.clues):
        st.markdown(f"{i+1}. {clue}")

# === Stemmesystem ===
if "karakterer" in game:
    st.subheader("🗳️ Afstemning: Hvem tror I er morderen?")
    vote_names = [char["navn"] for char in game["karakterer"]]
    selected_vote = st.radio("Vælg en mistænkt:", vote_names)
    if st.button("✅ Afgiv stemme"):
        st.session_state.votes[selected_vote] = st.session_state.votes.get(selected_vote, 0) + 1
        st.success(f"Stemmen er registreret for {selected_vote}!")

    if st.session_state.votes:
        st.markdown("### 📊 Stemmer indtil videre:")
        for name, count in st.session_state.votes.items():
            st.markdown(f"- {name}: {count} stemme(r)")

# === Afsløring ===
if st.button("🕵️ Thorups afsløring"):
    if not openai.api_key:
        st.warning("OpenAI-nøgle mangler.")
    else:
        with st.spinner("Inspector Thorup samler trådene..."):
            morder_navn = game.get("morder") or game.get("morderen") or "en ukendt person"
            afslør_prompt = f"I slutningen af et murder mystery afslører Inspector Thorup at {morder_navn} er morderen. Giv en dramatisk afsløring med motiv, reaktioner og beviser."
            final = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": afslør_prompt}]
            )
            st.success("Inspector Thorup siger:")
            st.markdown(final.choices[0].message.content)

# === PDF Print (karakterer og lokation) ===
def create_full_pdf(game_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, f"{game_data.get('titel', 'Murder Mystery')} - Spilpakke", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Tema: {game_data.get('tema')} - Årstid: {game_data.get('årstid')} - Lokation: {game_data.get('lokationstype')}", ln=True)
    pdf.ln(10)
    for c in game_data.get("karakterer", []):
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 10, f"{c['navn']} – {c['rolle']}", ln=True, fill=True)
        pdf.multi_cell(0, 8, f"Hemmelighed: {c['hemmelighed']}\nMål: {c['mål']}\n", border=1)
        pdf.ln(2)
    return pdf

if st.button("📄 Download hele spilpakken som PDF"):
    if game:
        pdf = create_full_pdf(game)
        pdf.output("spilpakke.pdf")
        with open("spilpakke.pdf", "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            link = f'<a href="data:application/pdf;base64,{base64_pdf}" download="spilpakke.pdf">Klik her for at hente PDF</a>'
            st.markdown(link, unsafe_allow_html=True)
