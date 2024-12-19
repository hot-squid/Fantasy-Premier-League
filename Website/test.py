# Include libraries
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO


current_week = datetime.now().isocalendar()[1]
gameweek = current_week - 34

# FPL API endpoint for general player information
fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

# Step 1: Fetch general data
response = requests.get(fpl_url)
data = response.json()
players = pd.DataFrame(data['elements'])

print(players.columns)


current_week = datetime.now().isocalendar()[1]
gameweek = current_week - 34

# FPL API endpoint for general player information
fpl_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

# Step 1: Fetch general data
response = requests.get(fpl_url)
fpl_data = response.json()
players_df = pd.DataFrame(fpl_data['elements'])

# Load the data for the specified Gameweek
data = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Players\Accumulated\Current_Form.csv')

# Ensure that 'Position' and 'Form' columns exist in your dataset
positions = data['Position'].unique()

top_players_list = []

# For each position, sort players by 'Form' in descending order and pick the top 5
for pos in positions:
    if pos == 'GK':
        pos_data = data[data['Position'] == pos].copy()
        pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
        top_1 = pos_data.head(1)
        top_players_list.append(top_1)
    elif pos == 'DEF':
        pos_data = data[data['Position'] == pos].copy()
        pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
        top_3 = pos_data.head(3)
        top_players_list.append(top_3)
    elif pos == 'MID':
        pos_data = data[data['Position'] == pos].copy()
        pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
        top_4 = pos_data.head(4)
        top_players_list.append(top_4)
    elif pos == 'FWD':
        pos_data = data[data['Position'] == pos].copy()
        pos_data = pos_data.sort_values(by='FDI_1', ascending=False)
        top_3 = pos_data.head(3)
        top_players_list.append(top_3)

# Concatenate all top 5 players per position into a single DataFrame
top_team = pd.concat(top_players_list, ignore_index=True)

print(top_team)


# Write ahead of gameweek
st.write(f'Ahead of Gameweek {gameweek}:')
# Iterate through the merged DataFrame to construct image URLs and display
for _, row in team.iterrows():
    player_code = row['code']
    player_name = f"{row['first_name']} {row['second_name']}"
    photo_url = f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{player_code}.png"
    
    # Fetch and display the image
    image_response = requests.get(photo_url)
    img = Image.open(BytesIO(image_response.content))
    
    # Display player name and image
    st.image(img, caption = player_name)
    