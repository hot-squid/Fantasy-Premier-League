import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import warnings
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
from datetime import datetime

# Model 2

# Get the current week number (1-52)
current_date = datetime.now().isocalendar()[1]
<<<<<<< HEAD
gameweek = current_date + 17
=======
gameweek = current_date + 18
>>>>>>> main

# Empty list to collect gameweek information
all_gameweeks = []

# Loop through each gameweek
for i in range(1, gameweek + 1):  # Adjusting the range to start from 1 to gameweek
    # Read the CSV for the current gameweek
    gameweek_data = pd.read_csv(rf'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Players\Seperate_GW\GW_{i}.csv')
    
    # Append the current gameweek data to the list
    all_gameweeks.append(gameweek_data)

# Concatenate all dataframes in the list into a single dataframe
data = pd.concat(all_gameweeks, axis=0, ignore_index=True)

# Drop unnamed column
data = data.drop(columns = ['Unnamed: 0'])

# Sort dataset by Player ID and Gameweek
final_data = data.sort_values(by=['Player ID', 'Gameweek'])

# Define the rolling window size
number_of_games = 4

# Calculate the rolling average of GW_Points over the specified number_of_games
final_data["Form"] = (
    final_data
    .groupby("Player ID")["GW Points"]
    .transform(lambda x: x.rolling(window=number_of_games).mean().round(3))
)

# Choose important columns
columns = [
    'Player ID', 'Name', 'Last_Name', 'Team', 'Position', 'Cost_Today',
    'GW Points', 'Form', 'Gameweek'
]

# Create final dataset
final_data = final_data[columns]

# Add fixture list into spreadsheet
fixtures = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Schedule\Fixtures.csv')

# Merge on fixture list
final_data = final_data.merge(fixtures, on= 'Team')

# Drop unneeded gameweek columns
def drop_gw_columns(final_data, weeks):
    # Create lists of columns to drop
    columns_to_drop = [f'GW{i}' for i in range(1, weeks + 1)] + [f'GW{i}' for i in range(weeks + 6, 39)]
    
    # Drop columns if they exist in the DataFrame
    final_data = final_data.drop(columns=[col for col in columns_to_drop if col in final_data.columns], errors='ignore')
    return final_data

# Run the loop
data = drop_gw_columns(final_data, gameweek)

# filter on current gameweek
today = data['Gameweek'].isin([gameweek])
data = data[today]

# Import improve fixture difficulty 
difficulty = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Difficulty_ratings\FD_IMPROVED\Current_FD_Improved.csv', index_col=0)

# Create a mapping dictionary from fixture difficulty
mapping = difficulty.set_index(['Opponent', 'Position'])['FD_combined'].to_dict()

# Map difficulty for NGWs (next gameweeks) using Team and Position
for i in range(1, 6):  # NGW1 to NGW5
    data[f'NGW{i}'] = data.apply(lambda row: mapping.get((row.iloc[8 + i], row.iloc[4]), None), axis=1)

# Loop to create FDI_1 to FDI_5, summing up the values from F_1 to F_i
for i in range(1, 6):
    # Create FDI_i by summing the appropriate columns
    data[f'F_{i}'] = data[[f'NGW{j}' for j in range(1, i+1)]].sum(axis=1)

# Calculate accumulated FD_index for up to next 5 gameweeks
for i in range(1, 6):
    data[f'FDI_{i}'] = round(data.iloc[:, 7] / data.iloc[:, 18 + i], 4)

# Export to csv for website
data.to_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Website\Current_form\Current_Form_M2.csv')

# Define constants
BUDGET = 800  # Choose your budget (1000 = £100m)
WEEKS = 1  # Choose how many weeks you want to prepare for between 1 and 5
GK = 1  # Goalkeepers required (Choose between 0 and 2)
DEF = 3  # Defenders required (Choose between 0 and 5)
MID = 4  # Midfielders required (Choose between 0 and 5)
FWD = 3  # Forwards required (Choose between 0 and 3)

# Dynamically create the column name based on the number of weeks
column_name = f'FDI_{WEEKS}'

# Filter out players with FD_index == 0 to avoid selecting them
data = data[data[column_name] > 0]

# Create lists of key variables
names = data.Last_Name.tolist()
teams = data.Team.tolist()
positions = data.Position.tolist()
prices = data.Cost_Today.tolist()
FD_index = data[column_name].tolist()

# Initialize the problem
prob = LpProblem("FPL_Player_Choices", LpMaximize)

# Create binary variables for players
players = [LpVariable(f"player_{i}", cat="Binary") for i in range(len(data))]

# Define the objective function: maximize the sum of FD_index for selected players
prob += lpSum(players[i] * FD_index[i] for i in range(len(data)))

# Budget constraint: the sum of selected players' prices must be <= BUDGET
prob += lpSum(players[i] * prices[i] for i in range(len(data))) <= BUDGET

# Budget lower bound constraint
prob += lpSum(players[i] * prices[i] for i in range(len(data))) >= (BUDGET - 75)

# Position constraints: enforce exact limits for each position
prob += lpSum(players[i] for i in range(len(data)) if positions[i] == 'GK') == GK
prob += lpSum(players[i] for i in range(len(data)) if positions[i] == 'DEF') == DEF
prob += lpSum(players[i] for i in range(len(data)) if positions[i] == 'MID') == MID
prob += lpSum(players[i] for i in range(len(data)) if positions[i] == 'FWD') == FWD

# Club constraint: each team can have at most 3 players
for club in data.Team.unique():
    prob += lpSum(players[i] for i in range(len(data)) if teams[i] == club) <= 3

# Solve the problem
prob.solve()

# Create a list of selected players
selected_players = []

for v in prob.variables():
    if v.varValue != 0:
        index = int(v.name.split("_")[1])
        player_info = {
            'Name': names[index],
            'Team': teams[index],
            'Position': positions[index],
            'FD_Index': FD_index[index],
            'Price': prices[index],
        }
        selected_players.append(player_info)

selected_players_df = pd.DataFrame(selected_players)

# Display the DataFrame
print(selected_players_df)

# Display the total cost and index
print(f'Total Team Cost:', sum(selected_players_df.Price))
print(f'Total Team Index', sum(selected_players_df.FD_Index))