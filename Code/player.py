
from load import FplApiDataRaw
import pandas as pd
import json

# Create data class 
data = FplApiDataRaw()

# Team info
teams = data.teams_json

# Access elements attribute
info = data.elements_json

# Get all available data
summary = data.get_all_element_summaries()

# Player details
cols = ['id', 'first_name', 'second_name', 'team', 'element_type']
player = pd.DataFrame(info).loc[:, cols]

# Team details
cols_2 = ['id', 'name', 'short_name']
team = pd.DataFrame(teams).loc[:, cols_2]

# Merge data
player = (
    player
    .merge(team[['id','name','short_name']],
           left_on='team', right_on='id', how='left', suffixes=('', '_team'))
    .rename(columns={'name': 'team_name', 'short_name': 'team_abbr'})
    .drop(columns=['team', 'id_team'])   # <-- note: not nested list
)

# Create mapping for positions
pos_map = {1: "GK", 2: "DEF", 3: "MID", 4: "FWD"}

# add a new column
player["position"] = player["element_type"].astype(int).map(pos_map)

# Drop columns
player.drop(columns= ['element_type'], inplace= True)

# Filter by current season and create pd dataframe
data = pd.DataFrame(summary['history'])

# Capitalize each column heading
data.columns = data.columns.str.capitalize()

# Rename columns
data.rename(columns={
    'Element': 'Player ID',
    'Goals_scored' : 'Goals',
    'Clean_sheets': 'Clean Sheets',
    'Goals_conceded': 'Goals Conceded',
    'Penalties_saved': 'Penalties Saved',
    'Penalties_missed': 'Penalties Missed',
    'Yellow_cards': 'YC',
    'Red_cards': 'RC',
    'Bonus': 'Total Bonus Points',
    'Bps': 'Total BPS', 
    'Ict_index': 'ICT Index',
    'Expected_goal_involvements': 'xGi',
    'Expected_goals_conceded': 'xGc',
    'Selected': 'Selected %', 
    'Transfers_in': 'Transfers In GW',
    'Transfers_out': 'Transfers Out GW',
    'Round': 'Gameweek',
    'Value': 'Cost_Today',
    'Total_points': 'GW Points',
    'Kickoff_time': 'KO_time',
    'Expected_goals':'xG',
    'Expected_assists': 'xA',
}, inplace=True)

# Select data to keep
columns = [
    'Player ID', 'Cost_Today', 'GW Points', 'Minutes', 'KO_time', 'Goals', 'Assists',
    'Clean Sheets', 'Goals Conceded', 'Penalties Saved', 'Penalties Missed', 'YC', 
    'RC', 'Saves', 'Total Bonus Points', 'Total BPS', 'Influence', 'Creativity', 
    'Threat', 'ICT Index', 'xG', 'xA', 'xGi', 'xGc', 'Transfers In GW', 
    'Transfers Out GW', 'Gameweek'
]

# Filter by selected data
data = data[columns]

# Rename categories 
player.rename(columns={'id':'Player ID', 'first_name':'Name', 'second_name':'Last_Name', 'team_name':'Team', 'position': 'Position'}, inplace= True)

# Merging all player data on Player ID
dataset = player.merge(data, on='Player ID', how='left')

# Collect availablilty data 
avail = []
for player in info:
    play = player['id']
    status = player['status']
    avail.append([play, status])

# Turn into a pandas dataframe
availability = pd.DataFrame(avail, columns= ['Player ID', 'Avail'])

# Merge with other dataframe
dataset = dataset.merge(availability, on= 'Player ID')

# Import fixture information
fixtures = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Fixtures\Schedule\Fixtures.csv')

# Use 'melt' function to unpivot the dataframe
fixtures = fixtures.melt(id_vars=['Team'], var_name='Gameweek', value_name='Opponent')

# Remove 'GW' prefix and convert the GW number to an integer 
fixtures['Gameweek'] = fixtures['Gameweek'].str.replace('GW', '').astype(int)

# Merge fixture data to the player data
data= pd.merge(dataset, fixtures, on=['Team', 'Gameweek'], how='left')

# Import fixture difficulty information
fixture_diff = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Fixtures\Difficulty_ratings\FD_FPL\Difficulty.csv')

# Create a mapping dictionary from fixture difficulty
mapping = fixture_diff.set_index('Fixture')['Difficulty'].to_dict()

# Convert fixture with the integer difficulty
data['Difficulty'] = data['Opponent'].map(mapping)

# Create function to filter by gameweek
def filter_data_by_round(df, gameweek):
    # Ignore the first row by slicing the DataFrame
    filtered_data = df.iloc[1:]  # Skip the first row
    return filtered_data[filtered_data['Gameweek'] == gameweek]

# Current gameweek
current_gw = int(data['Gameweek'].max())

# Filter by current gameweek 
GW = filter_data_by_round(data, current_gw)

# Create a full file path with the current gameweek
file_path = fr'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Players\GW_{current_gw}.csv'

# Export the current working dataset to the specified file path
GW.to_csv(file_path, index=False)