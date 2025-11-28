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

def pick_top_and_bench(form_df: pd.DataFrame, position: str, top_n: int, taken_ids: set, bench_each: int = 1):
    """Pick top_n starters for a position and bench_each bench players, excluding any already taken_ids."""
    pool = form_df[form_df["Position"] == position].copy()
    if pool.empty:
        return pd.DataFrame(), pd.DataFrame()

    pool = pool.sort_values("FDI_1", ascending=False)

    # starters: first top_n not already taken
    starters = pool[~pool["Player ID"].isin(taken_ids)].head(top_n)
    taken_now = set(starters["Player ID"].tolist())

    # bench: next-best not in starters or previously taken
    exclude_ids = taken_ids.union(taken_now)
    bench = pool[~pool["Player ID"].isin(exclude_ids)].head(bench_each)

    # update taken set for caller
    taken_ids |= taken_now
    taken_ids |= set(bench["Player ID"].tolist())

    return starters, bench

# --- Main UI
def run_XI():

    # Header shows a GW label (no user input / no cycling)
    current_week = datetime.now().isocalendar()[1]
    gw_label = max(1, current_week - 35)
    st.header(f"Des's Hot Picks GW{int(gw_label)}")

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

    # --- Select XI and Bench (distinct)
    taken_ids: set = set()

    gk_top,  gk_bench  = pick_top_and_bench(form_df, "GK",  1, taken_ids, bench_each=1)
    def_top, def_bench = pick_top_and_bench(form_df, "DEF", 3, taken_ids, bench_each=1)
    mid_top, mid_bench = pick_top_and_bench(form_df, "MID", 4, taken_ids, bench_each=1)
    fwd_top, fwd_bench = pick_top_and_bench(form_df, "FWD", 3, taken_ids, bench_each=1)

    top_team = pd.concat([gk_top, def_top, mid_top, fwd_top], ignore_index=True)
    bench_team = pd.concat([gk_bench, def_bench, mid_bench, fwd_bench], ignore_index=True)

    # Merge to get names/codes from bootstrap
    team = top_team.merge(players, left_on="Player ID", right_on="id", how="left")
    bench = bench_team.merge(players, left_on="Player ID", right_on="id", how="left")

    # Split by FPL element_type (1 GK, 2 DEF, 3 MID, 4 FWD)
    gk          = team[team["element_type"] == 1]
    defenders   = team[team["element_type"] == 2]
    midfielders = team[team["element_type"] == 3]
    forwards    = team[team["element_type"] == 4]

    image_width = 70

    # --- GK (center column, no enumerate)
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

    # --- Bench (distinct already ensured)
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
        st.info("Best XI by FDI_1 in a 3–4–3 from the current dataset, plus a 4-player bench (GK/DEF/MID/FWD) from the next-best, with no duplicates.")
