import pandas as pd
import streamlit as st
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

FPL_BOOTSTRAP = "https://fantasy.premierleague.com/api/bootstrap-static/"
FORM_CSV = "https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.csv"

@st.cache_data(show_spinner=False)
def fetch_bootstrap():
    r = requests.get(FPL_BOOTSTRAP, timeout=15)
    r.raise_for_status()
    data = r.json()
    players_df = pd.DataFrame(data["elements"])
    return players_df

@st.cache_data(show_spinner=False)
def fetch_form_csv():
    df = pd.read_csv(FORM_CSV)
    return df

def get_player_image(player_code: int, timeout: int = 6):
    url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None  # fall back to name-only

def run_XI():
    # Work out a default GW label but let the user override if they want
    current_week = datetime.now().isocalendar()[1]
    default_gameweek = max(1, current_week - 33)
    gameweek = st.number_input("Gameweek", min_value=1, max_value=3)