import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import random
import pingouin as pg
import glob
import re
import warnings

# Model 2.1

# Ignore all warnings
warnings.filterwarnings("ignore")

# Current gameweek parameter
gameweek = 15

# Initialize an empty list to store all individual, player gameweek data 
all_player_sep = []

# Loop through each gameweek
for i in range(1, gameweek + 1):  # Adjusting the range to start from 1 to gameweek
    # Read the CSV for the current gameweek
    x = pd.read_csv(rf'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Players\Seperate_GW\GW_{i}.csv')
    
    # Append the current gameweek data to the list
    all_player_sep.append(x)

# Concatenate all dataframes in the list into a single dataframe
player_data = pd.concat(all_player_sep, axis=0, ignore_index=True)

# Drop unnamed column
player_data = player_data.drop(columns = ['Unnamed: 0'])

# Sort dataset correctly IMPORTANT
player_data = player_data.sort_values(by= ['Player ID','Gameweek'])

# Add fixture list into spreadsheet
fixtures = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Schedule\Fixtures.csv')

# Merge on fixture list
final_data = player_data.merge(fixtures, on= 'Team')

team_data = []

# For all available gameweeks
for gameweek in range (4,15):

    # Drop unneeded gameweek columns
    def drop_gw_columns(final_data, gameweek):
        # Create lists of columns to drop
        columns_to_drop = [f'GW{i}' for i in range(1, gameweek + 1)] + [f'GW{i}' for i in range(gameweek + 6, 39)]
        
        # Drop columns if they exist in the DataFrame
        final_data = final_data.drop(columns=[col for col in columns_to_drop if col in final_data.columns], errors='ignore')
        return final_data

    # Run the loop
    player_data = drop_gw_columns(final_data, gameweek)

    # Read the difficulty data
    difficulty = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Difficulty_ratings\FD_IMPROVED\Current_FD_Improved.csv', index_col=0)

    # Create a mapping dictionary
    mapping = difficulty.set_index(['Opponent', 'Position'])['FD_combined'].to_dict()

    # Apply the mapping to a new column in player_data
    player_data['FD_combined'] = player_data.apply(
        lambda row: mapping.get((row['Opponent'], row['Position']), None), axis=1
    )

    # Map difficulty for NGWs (next gameweeks) using Team and Position
    for i in range(1, 6):  # NGW1 to NGW5
        player_data[f'NGW{i}'] = player_data.apply(lambda row: mapping.get((row.iloc[32 + i], row.iloc[4]), None), axis=1)

    # Specify the path to the files
    defense = glob.glob(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Team\Seperate_GW\Defensive\*.csv')

    # Define a function to extract the week number from the filename
    def extract_week_number(filename):
        match = re.search(r'GW_(\d+)', filename)
        return int(match.group(1)) if match else None

    # Read each defensive file and add the 'Week' column
    def_weekly_data = pd.concat(
        [pd.read_csv(file).assign(Week=extract_week_number(file)) for file in defense],
        ignore_index=True
    )
    # Remove 'VS' team from defensive data
    def_weekly_data['Team'] = def_weekly_data['Team'].str[3:]

    # Choose columns data 
    columns_new = ['Team','Week', 'Playing TimeMP', 'Possession','PerformanceGls','PerformanceAst','ExpectedxG','ExpectedxAG',
                'Per 90 MinutesGls','Per 90 MinutesAst','Per 90 MinutesxG','Per 90 MinutesxAG']

    # Specify the path to the files
    defense = glob.glob(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Team\Seperate_GW\Defensive\*.csv')

    # Define a function to extract the week number from the filename
    def extract_week_number(filename):
        match = re.search(r'GW_(\d+)', filename)
        return int(match.group(1)) if match else None

    # Read each defensive file and add the 'Week' column
    def_weekly_data = pd.concat(
        [pd.read_csv(file).assign(Week=extract_week_number(file)) for file in defense],
        ignore_index=True
    )
    # Remove 'VS' team from defensive data
    def_weekly_data['Team'] = def_weekly_data['Team'].str[3:]

    # Choose columns data 
    columns_new = ['Team','Week', 'Playing TimeMP', 'Possession','PerformanceGls','PerformanceAst','ExpectedxG','ExpectedxAG',
                'Per 90 MinutesGls','Per 90 MinutesAst','Per 90 MinutesxG','Per 90 MinutesxAG']

    # Defensive data
    defensive_data = pd.DataFrame(def_weekly_data[columns_new]).sort_values(by = 'Week')

    # Collect fixture list
    fixtures = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Schedule\Fixtures_alt_names.csv')

    # Create function to collect fixture data
    def fixture_data(team, fixtures, gameweek):
        
        # Create empty list of fixtures
        fix_data = []
        # Iterate over each row of the fixtures DataFrame
        for index, row in fixtures.iterrows():
            # Check if the row's team matches the input team
            if row['Team'] == team:
                # Loop through the columns corresponding to gameweeks
                for col in fixtures.columns[1:gameweek + 1]:
                    if '(H)' or '(A)' in row[col]:  # Check row has fixture information
                        fix_data.append([col, row[col]])

        # Return the collected home data
        return fix_data

    # Get games
    games = []

    # List of unique teams 
    teams = defensive_data['Team'].unique()

    # For all teams
    for team in teams:
        # Get fixture information
        fix_data = fixture_data(team, fixtures, gameweek)  # Fetch data for the team
        for info in fix_data:
            # You can extract relevant information from 'game', like opponent, week, etc.
            games.append([info[0], team, info[1]])

    # Creating DataFrame for all teams fixture list
    fix = pd.DataFrame(games, columns=['Week', 'Team', 'Opponent'])

    # Remove 'GW' from the 'Week' string and convert it to an integer
    fix['Week'] = fix['Week'].str[2:].astype(int)

    # Define columns
    cols = ['Team', 'Week', 'Possession', 'PerformanceGls',
        'PerformanceAst', 'ExpectedxG', 'ExpectedxAG', 'Per 90 MinutesGls',
        'Per 90 MinutesAst', 'Per 90 MinutesxG', 'Per 90 MinutesxAG']

    # get defensive data
    defensive = defensive_data[cols]

    # rename defensive
    defensive = defensive.rename(columns = {'PerformanceGls': 'Team_gls_against',
                                                    'ExpectedxG': 'TeamxG_against'})

    # Collect columns that are averages of team performance (per_90)
    Per_90 = defensive[['Team', 'Week', 'Per 90 MinutesxG','Per 90 MinutesGls']]

    # Filter on latest GW possible to get most accurate average value
    Per_90 = Per_90[Per_90['Week'] == 8]

    # All data
    expanded_data = []

    # Loop through gameweeks 1 to 8
    for week in range(1, 8):
        for _, row in Per_90.iterrows():
            expanded_data.append({
                'Team': row['Team'],
                'Week': week,
                'Per 90 MinutesxG': row['Per 90 MinutesxG'],
                'Per 90 MinutesGls': row['Per 90 MinutesGls']
            })

    # Create a dataframe
    data = pd.DataFrame(expanded_data)

    data = data.rename(columns = {'Per 90 MinutesGls': 'Team_gls_against',
                                                    'Per 90 MinutesxG': 'TeamxG_against'})

    # Merge the team data
    complete = pd.concat([defensive, data])

    # Merge defensive data for each team for each gameweek
    team_defense = fix.merge(complete, on=['Team', 'Week'])

    # Keep useable columns
    team_defense = team_defense[['Week', 'Team', 'Opponent', 'Team_gls_against', 'TeamxG_against']]

    # Define a dictionary of old team names as keys and new names as values
    name_changes = {
        "Nott'ham Forest": 'Nottingham Forest',
        'Manchester Utd': 'Man Utd',
        'Manchester City': 'Man City',
        'Newcastle Utd': 'Newcastle',
        'Leicester City': 'Leicester',
        'Ipswich Town': 'Ipswich',
        'Tottenham': 'Spurs',
        
    }
    # Replace the team names using the dictionary
    team_defense['Team'] = team_defense['Team'].replace(name_changes)

    # Rename team columns
    team_defense.rename(columns={'Week against': 'Week', 'Team against': 'Team', 'Opponent against': 'Opponent'}, inplace=True)

    # Merge the playerdata with attacking, and then defensive team information
    player_d = pd.merge(player_data, team_defense, on=['Team', 'Opponent'], how='left')

    # Drop uneeded columns
    player_data = player_d.drop(columns = ['KO_time'])

    columns_to_drop = ['Goals', 'Assists', 'Clean Sheets',
        'Goals Conceded', 'Penalties Saved', 'Penalties Missed', 'YC', 'RC',
        'Saves', 'Total Bonus Points', 'Total BPS', 'Influence', 'Creativity',
        'Threat', 'ICT Index', 'xA', 'xGi', 'xGc', 'Transfers In GW',
        'Transfers Out GW', 'Opponent', 'Difficulty',
        'FD_combined']

    # New player data with columns
    player_data = player_data.drop(columns=columns_to_drop)

    # Create opponent difficulty rating (same as fixture difficulty)
    for i in range(1, 6):
        player_data[f'Opponent_Difficulty{i}'] = player_data[f'NGW{i}'].rename(inplace= True)
        
    # Create a dictionary to store the difficulty data for each gameweek
    opponent_difficulties = {}

    # Loop to precompute opponent difficulty for all gameweeks (1 to 5)
    for i in range(1, 6):
        # Store the NGW{i} difficulty values into a new dictionary for each gameweek
        opponent_difficulties[f'Opponent_Difficulty{i}'] = player_data[f'NGW{i}']

    # Add opponent difficulty columns to the player_data dataframe
    for i in range(1, 6):
        player_data[f'Opponent_Difficulty{i}'] = opponent_difficulties[f'Opponent_Difficulty{i}']

    # Step 2: Calculate player difficulty for all gameweeks at once, avoiding iterrows()
    player_difficulty_summary = []

    # Loop through gameweeks from gameweek+1 to gameweek+5
    for i in range(gameweek + 1, gameweek + 6):
        # For each gameweek, compute the difficulty for all players based on position
        difficulty_values = []

        # Vectorized operation to compute difficulty for all players for this gameweek
        for _, row in player_data.iterrows():
            team = row['Team']
            player_position = row['Position']
            opponent_info = row[f'GW{i}']

            # Filter difficulty list for the player's team
            difficulty_filtered = difficulty[difficulty['Team'] == team]
            
            # Determine if the player played at home or away
            if "(H)" in opponent_info:
                player = difficulty_filtered[difficulty_filtered['Opponent'].str.contains(r"\(A\)")]
            elif "(A)" in opponent_info:
                player = difficulty_filtered[difficulty_filtered['Opponent'].str.contains(r"\(H\)")]
            else:
                continue  # Skip if opponent info is neither (H) nor (A)

            # Determine difficulty based on player position
            if player_position in ['MID', 'FWD']:
                difficulty_player = player[player['Position'] == 'DEF']  # MID or FWD face DEF opponents
            elif player_position in ['GK', 'DEF']:
                difficulty_player = player[player['Position'] == 'FWD']  # GK or DEF face FWD opponents
            else:
                continue  # Skip if position is not recognized

            # Collect the value that remains after filtering away irrelevant information
            score = difficulty_player['FD_combined'].sum()

            # Store the difficulty result
            difficulty_values.append(score)

        # Add the difficulty values for this gameweek to the player_data dataframe
        player_data[f'Player_Difficulty{i - gameweek}'] = difficulty_values

    # Create difficulty difference for all weeks
    for i in range(1, 6):
    # Create difficulty difference
        player_data[f'F_Difference{i}'] = player_data[f'Player_Difficulty{i}'] - player_data[f'Opponent_Difficulty{i}']

    number_of_games = 4  # Define the rolling window size

    # Apply rolling mean for "Form_xG" (including current gameweek)
    player_data["Form_player_xG"] = (
        player_data.groupby("Player ID")["xG"]
        .transform(lambda x: x.rolling(window=number_of_games).mean().round(3))
    )

    # Apply rolling mean for "Form_TeamxG_against" (including current gameweek)
    player_data["Form_TeamxG_against"] = (
        player_data.groupby("Player ID")["TeamxG_against"]
        .transform(lambda x: x.rolling(window=number_of_games).mean().round(3))
    )

    # Min/Max scaler 
    scaler = MinMaxScaler(feature_range=(2, 5))

    # Reshape the data to a 2D array and apply the scaler
    for i in range(1,6):
        player_data[f'FD_Difference_norm{i}'] = scaler.fit_transform(player_data[f'F_Difference{i}'].values.reshape(-1, 1))

    # Player xG_form
    player_data[f'Form_player_xG_norm'] = scaler.fit_transform(player_data['Form_player_xG'].values.reshape(-1, 1))

    # Team xG_against_form
    player_data[f'Form_TeamxG_against_norm'] = scaler.fit_transform(player_data['Form_TeamxG_against'].values.reshape(-1, 1))

    # Creating interaction variables for defensive and attacking players
    for i in range(1, 6):
        player_data[f'FD{i}'] = player_data.apply(
            lambda row: (
                row[f'FD_Difference_norm{i}'] / row['Form_TeamxG_against_norm']
                if row['Position'] in ['GK', 'DEF']
                else row[f'FD_Difference_norm{i}'] * row['Form_player_xG_norm']
            ),
            axis=1
        )

    # Loop to create FDI_1 to FDI_5, summing up the values from FD_1 to FD_i
    for i in range(1, 6):
        player_data[f'FDI_{i}'] = player_data[[f'FD{j}' for j in range(1, i + 1)]].sum(axis=1)

    # Filter on columns
    columns = ['Player ID', 'Name', 'Last_Name', 'Team', 'Position', 'Cost_Today', 
            'Minutes', 'Gameweek','Form_player_xG_norm','Form_TeamxG_against_norm', 'FDI_1',
        'FDI_2', 'FDI_3', 'FDI_4', 'FDI_5']

    # Filter on columns
    player_data = player_data[columns]

    # Remove players who play less than 61 minutes in a game (i.e. they do not recieve their 2 points minimum for playoing this amount)
    player_data = player_data[player_data['Minutes'] > 60].copy()

    # Filter on current gameweek 
    player_data = player_data[player_data['Gameweek'] == gameweek].copy()

    # Pull in dataset
    data = player_data

    # Define constants
    BUDGET = 800 # Choose your budget (1000 = £100m)
    WEEKS = 1 # Choose how many weeks you want to prepare for between 1 and 5
    GK = 1 # Goalkeepers required (Choose between 0 and 2)
    DEF = 3 # Defenders required (Choose between 0 and 5)
    MID = 4 # Midfielders required (Choose between 0 and 5)
    FWD = 3 # Forwards required (Choose between 0 and 3)

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
                names[index],
                #'Team': teams[index],
                #'Position': positions[index],
                #'FD_Index': FD_index[index],
                #'Price': prices[index],
            }
            selected_players.append(player_info)

    # Create team data folder 
    team_data.append(selected_players)

# Create dataframe
data = pd.DataFrame(team_data)

# Export to csv
data.to_csv('data.csv')


