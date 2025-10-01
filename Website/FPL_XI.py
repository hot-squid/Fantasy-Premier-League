# --- Imports
import pandas as pd
import streamlit as st
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# --- Constants
FPL_BOOTSTRAP = "https://fantasy.premierleague.com/api/bootstrap-static/"
FORM_CSV = "https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.csv"

# --- Data loaders (cached)
@st.cache_data(show_spinner=False)
def fetch_bootstrap():
    r = requests.get(FPL_BOOTSTRAP, timeout=15)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data["elements"])

@st.cache_data(show_spinner=False)
def fetch_form_csv():
    return pd.read_csv(FORM_CSV)

# --- Helpers
def get_player_image(player_code: int, timeout: int = 6):
    """Return PIL.Image or None on failure."""
    url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return Image.open(BytesIO(r.content))
    except Exception:
        return None

def safe_name(row) -> str:
    return f"{row.get('first_name','').strip()} {row.get('second_name','').strip()}".strip()

def top_n_by(df: pd.DataFrame, n: int, col: str = "FDI_1") -> pd.DataFrame:
    return df.sort_values(col, ascending=False).head(n)

# --- Main UI
def run_XI():

    # Gameweek label (keep your original logic but allow override)
    current_week = datetime.now().isocalendar()[1]
    default_gw = max(1, current_week - 33)
    gameweek = st.number_input("Gameweek", min_value=1, max_value=38, value=default_gw, step=1)
    st.header(f"Des's Hot Picks GW{int(gameweek)}")

    # Load data
    try:
        players = fetch_bootstrap()
        form_df = fetch_form_csv()
    except Exception as e:
        st.error(f"Couldn't load data: {e}")
        return

    # Validate CSV structure
    required = {"Player ID", "Position", "FDI_1"}
    missing = required - set(form_df.columns)
    if missing:
        st.error(f"Form CSV missing required columns: {missing}")
        return

    # XI selection: 3-4-3 by FDI_1
    gk_top  = top_n_by(form_df[form_df["Position"] == "GK"], 1)
    def_top = top_n_by(form_df[form_df["Position"] == "DEF"], 3)
    mid_top = top_n_by(form_df[form_df["Position"] == "MID"], 4)
    fwd_top = top_n_by(form_df[form_df["Position"] == "FWD"], 3)

    # Bench: next-best GK/DEF/MID/FWD (1 each)
    gk_bench  = top_n_by(form_df[form_df["Position"] == "GK"].iloc[1:], 1)
    def_bench = top_n_by(form_df[form_df["Position"] == "DEF"].iloc[3:], 1)
    mid_bench = top_n_by(form_df[form_df["Position"] == "MID"].iloc[4:], 1)
    fwd_bench = top_n_by(form_df[form_df["Position"] == "FWD"].iloc[3:], 1)

    top_team = pd.concat([gk_top, def_top, mid_top, fwd_top], ignore_index=True)
    bench_team = pd.concat([gk_bench, def_bench, mid_bench, fwd_bench], ignore_index=True)

    # Merge to get names/codes from bootstrap
    team = top_team.merge(players, left_on="Player ID", right_on="id", how="left")
    bench = bench_team.merge(players, left_on="Player ID", right_on="id", how="left")

    # Split by FPL element_type (1 GK, 2 DEF, 3 MID, 4 FWD)
    gk         = team[team["element_type"] == 1]
    defenders  = team[team["element_type"] == 2]
    midfielders= team[team["element_type"] == 3]
    forwards   = team[team["element_type"] == 4]

    image_width = 70

    # --- GK (center column)
    gk_cols = st.columns([1, 1, 1])
    if not gk.empty:
        row = gk.iloc[0]
        name = safe_name(row)
        img = get_player_image(int(row["code"])) if pd.notna(row.get("code")) else None
        if img:
            gk_cols[1].image(img, caption=name, width=image_width)
        else:
            gk_cols[1].markdown(f"**{name}**")

    # --- DEF (3 across)
    def_cols = st.columns(3)
    for i, (_, row) in enumerate(defenders.head(3).iterrows()):
        name = safe_name(row)
        img = get_player_image(int(row["code"])) if pd.notna(row.get("code")) else None
        if img:
            def_cols[i].image(img, caption=name, width=image_width)
        else:
            def_cols[i].markdown(f"**{name}**")

    # --- MID (4 across)
    mid_cols = st.columns(4)
    for i, (_, row) in enumerate(midfielders.head(4).iterrows()):
        name = safe_name(row)
        img = get_player_image(int(row["code"])) if pd.notna(row.get("code")) else None
        if img:
            mid_cols[i].image(img, caption=name, width=image_width)
        else:
            mid_cols[i].markdown(f"**{name}**")

    # --- FWD (3 across)
    fwd_cols = st.columns(3)
    for i, (_, row) in enumerate(forwards.head(3).iterrows()):
        name = safe_name(row)
        img = get_player_image(int(row["code"])) if pd.notna(row.get("code")) else None
        if img:
            fwd_cols[i].image(img, caption=name, width=image_width)
        else:
            fwd_cols[i].markdown(f"**{name}**")

    # --- Bench
    st.write(""); st.write("")
    st.subheader("Bench")
    bench_image_width = 50

    if len(bench) > 0:
        bench_cols = st.columns(len(bench))
        for i, (_, row) in enumerate(bench.iterrows()):
            name = safe_name(row)
            img = get_player_image(int(row["code"])) if pd.notna(row.get("code")) else None
            if img:
                bench_cols[i].image(img, caption=name, width=bench_image_width)
            else:
                bench_cols[i].markdown(f"**{name}**")
    else:
        st.write("No bench players selected.")

    with st.expander("Information"):
        st.info("Des LynAIm's picks by highest FDI_1 in a 3–4–3, plus a 4-player bench from next-best GK/DEF/MID/FWD.")
