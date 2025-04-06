# Murder Mystery AI Agent - Mobilvenlig App-version med lyd, billeder og interaktion

import streamlit as st
import random
from typing import List, Dict
import base64
from fpdf import FPDF
import requests

st.set_page_config(page_title="Murder Mystery AI", layout="centered")

# === Mobilvenlig styling ===
st.markdown("""
    <style>
    body, html, .main, .block-container {
        max-width: 100% !important;
        padding: 1rem;
    }
    .character-card {
        background-color: #f9f9f9;
        border-left: 5px solid #444;
        padding: 10px;
        margin-bottom: 15px;
        border-radius: 8px;
    }
    .room-card {
        background-color: #eef1f5;
        padding: 10px;
        border-radius: 6px;
        margin: 4px 0;
        font-weight: bold;
        font-size: 1.1rem;
    }
    h1, h2, h3, h4 {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# === Simpel game-generator (demo data) ===
def generate_game():
    return {
        "theme": "Kostskole i 1960'erne",
        "season": "Efterår"
    }

game = generate_game()

# === Billedgenerator (tema-baseret kort) ===
def get_location_image(theme: str):
    prompt = f"A 2D illustrated floor plan of a {theme.lower()}, top-down view, cozy and mysterious style, perfect for a murder mystery board game"
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    return url

# === Musikgenerator (tema og årstid) ===
def get_ambient_audio(theme: str, season: str):
    return f"https://www.fesliyanstudios.com/play-mp3/387"  # Mystery ambience (royalty-free)

# === Lokationskort og billede ===
st.subheader("🗺️ Lokationskort")

def generate_rooms(theme: str):
    if "slot" in theme.lower():
        return ["🏰 Storsal", "📚 Bibliotek", "🍷 Vinkælder", "🕯️ Tårnværelse", "🌳 Have"]
    elif "kostskole" in theme.lower():
        return ["🍽️ Spisesal", "🧑‍🏫 Rektors kontor", "🛏️ Sovesal", "📁 Arkiv", "🔦 Kældergang"]
    elif "rum" in theme.lower():
        return ["🎛️ Kontrolrum", "🚀 Sovekabine", "📦 Lastboks", "🧪 Laboratorium", "🔧 Maskinrum"]
    elif "byvilla" in theme.lower():
        return ["🛋️ Stue", "🍳 Køkken", "📖 Arbejdsværelse", "🌿 Vinterhave", "🔒 Kælderrum"]
    else:
        return ["🏠 Hovedsal", "🛌 Gæsteværelse", "🔐 Kælderrum", "🌲 Have", "📦 Depot"]

location_rooms = generate_rooms(game["theme"])
st.markdown("**Områder til udforskning:**")
for room in location_rooms:
    st.markdown(f"<div class='room-card'>{room}</div>", unsafe_allow_html=True)

st.markdown("**Visualisering af lokationen:**")
image_url = get_location_image(game["theme"])
st.image(image_url, caption=f"Visualisering: {game['theme']}", use_column_width=True)

# === Stemningsmusik ===
st.subheader("🎶 Stemningsmusik")
audio_url = get_ambient_audio(game["theme"], game["season"])
st.audio(audio_url, format="audio/mp3")
