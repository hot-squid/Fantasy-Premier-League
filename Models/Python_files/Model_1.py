import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum

# Model 1

# Define global parameters
Gameweek = 14
BUDGET = 800 
WEEKS = 1 
GK = 1
DEF = 3
MID = 4 
FWD = 3 

# Read csv dataframe
data = pd.read_csv(rf'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Players\Accumulated\GW_{Gameweek}.csv', index_col=0)

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

# Budget constraint: the sum of selected players' prices must be <= BUDGET
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

# Convert selected players to a DataFrame for a better display
selected_players_df = pd.DataFrame(selected_players)

# Display the DataFrame
print(selected_players_df)

# Display the total cost and index
print(f'Total Team Cost:', sum(selected_players_df.Price))
print(f'Total Team Index', sum(selected_players_df.FD_Index))
