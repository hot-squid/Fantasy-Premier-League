# Include libraries
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

def run_XI():

    current_week = datetime.now().isocalendar()[1]
    gameweek = current_week + 17

    # Pitch of players
    st.header(f"Des's Hot Picks: GW{gameweek + 1}")
   
    # FPL API endpoint for general player information
    fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

    # Step 1: Fetch general data
    response = requests.get(fpl_url)
    data = response.json()
    players = pd.DataFrame(data['elements'])


    current_week = datetime.now().isocalendar()[1]
    gameweek = current_week - 34

    # FPL API endpoint for general player information
    fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

    # Step 1: Fetch general data
    response = requests.get(fpl_url)
    fpl_data = response.json()
    players_df = pd.DataFrame(fpl_data['elements'])

    # Load the data for the specified Gameweek
    data = pd.read_csv(r'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.1.csv')

    # Ensure that 'Position' and 'Form' columns exist in your dataset
    positions = data['Position'].unique()

    top_players_list = []
    bench_player_list = []

    # For each position, sort players by 'Form' in descending order and pick the top
    for pos in positions:
        if pos == 'GK':
            pos_data = data[data['Position'] == pos].copy()
            pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
            top_1 = pos_data.head(1)
            top_players_list.append(top_1)
            bench_1 = pos_data.iloc[2:3]
            bench_player_list.append(bench_1)
        elif pos == 'DEF':
            pos_data = data[data['Position'] == pos].copy()
            pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
            top_3 = pos_data.head(3)
            top_players_list.append(top_3)
            bench_2 = pos_data.iloc[3:5]
            bench_player_list.append(bench_2)
        elif pos == 'MID':
            pos_data = data[data['Position'] == pos].copy()
            pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
            top_4 = pos_data.head(4)
            top_players_list.append(top_4)
            bench_1 = pos_data.iloc[4:5]
            bench_player_list.append(bench_1)
        elif pos == 'FWD':
            pos_data = data[data['Position'] == pos].copy()
            pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
            top_3 = pos_data.head(3)
            top_players_list.append(top_3)
            bench_2 = pos_data.iloc[0]
            bench_player_list.append(bench_2)
            

    # Concatenate all top players per position into a single DataFrame
    top_team = pd.concat(top_players_list, ignore_index=True)

    # Including bench players
    bench_team = pd.concat(bench_player_list, ignore_index= True)

    # Combined
    team = top_team.merge(players, left_on= 'Player ID', right_on= 'id')
    bench = bench_team.merge(players, left_on='Player ID', right_on= 'id')

    # Separate players by position
    gk = team[team['element_type'] == 1]        # Goalkeepers
    defenders = team[team['element_type'] == 2] # Defenders
    midfielders = team[team['element_type'] == 3] # Midfielders
    forwards = team[team['element_type'] == 4]  # Forwards

    # Adjusted image width
    image_width = 70

    # GK: Position in the middle
    gk_cols = st.columns([1,1,1])  # three columns, GK will be in the middle
    for _, row in gk.iterrows():
        player_code = row['code']
        player_name = f"{row['first_name']} {row['second_name']}"
        photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        image_response = requests.get(photo_url)
        img = Image.open(BytesIO(image_response.content))
        gk_cols[1].image(img, caption=player_name, width=image_width)  # middle column is index 1

    # DEF row (3 columns)
    def_cols = st.columns([1,1,1])
    for i, (_, row) in enumerate(defenders.head(3).iterrows()):
        player_code = row['code']
        player_name = f"{row['first_name']} {row['second_name']}"
        photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        image_response = requests.get(photo_url)
        img = Image.open(BytesIO(image_response.content))
        def_cols[i].image(img, caption=player_name, width=image_width)

    # MID row (4 columns)
    mid_cols = st.columns([1,1,1,1])
    for i, (_, row) in enumerate(midfielders.head(4).iterrows()):
        player_code = row['code']
        player_name = f"{row['first_name']} {row['second_name']}"
        photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        image_response = requests.get(photo_url)
        img = Image.open(BytesIO(image_response.content))
        mid_cols[i].image(img, caption=player_name, width=image_width)

    # FWD row (3 columns)
    fwd_cols = st.columns([1,1,1])
    for i, (_, row) in enumerate(forwards.head(3).iterrows()):
        player_code = row['code']
        player_name = f"{row['first_name']} {row['second_name']}"
        photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
        image_response = requests.get(photo_url)
        img = Image.open(BytesIO(image_response.content))
        fwd_cols[i].image(img, caption=player_name, width=image_width)

    # Add vertical spacing before showing the bench
    st.write("")
    st.write("")
    st.write("")  # Add as many empty lines as needed

    st.subheader("Bench")

    # Make bench players smaller
    bench_image_width = 50  # Smaller width than main team images
    bench_count = len(bench)

    if bench_count > 0:
        # Slightly tighten columns by reducing the gap
        bench_cols = st.columns(bench_count, gap="small")
        for i, (_, row) in enumerate(bench.iterrows()):
            player_code = row['code']
            player_name = f"{row['first_name']} {row['second_name']}"
            photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
            image_response = requests.get(photo_url)
            img = Image.open(BytesIO(image_response.content))
            bench_cols[i].image(img, caption=player_name, width=bench_image_width)
    else:
        st.write("No bench players selected.")

    # Provide help tab if user needs
    with st.expander("Information"):
        st.info("Des LynAIm's picks without any constraints.")

