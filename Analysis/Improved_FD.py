import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from scipy.stats import boxcox, zscore, norm, gaussian_kde

all_gameweeks = []

files = os.listdir(
    r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Players'
)

for i in range(len(files)):
    gameweek_data = pd.read_csv(
        rf'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Players\GW_{i + 1}.csv'
    )
    all_gameweeks.append(gameweek_data)

data = pd.concat(all_gameweeks, ignore_index=True)

gameweek = len(files)

# Remove players who play less than 61 minutes in a game (i.e. they do not recieve their 2 points minimum for playoing this amount)
player_data = data[data['Minutes'] > 60].copy()

# Calculate frequencies of GW Points for all opponents
overall_frequency = (
    player_data['GW Points']
    .value_counts()
    .sort_index()
    .reset_index(name='Total')
)
overall_frequency.rename(columns={'index': 'GW Points'}, inplace=True)

# Initialize an empty list to store frequencies for each opponent
opponent_frequencies = []

# Get unique opponents and sort alphabetically
opponents = sorted(player_data['Opponent'].unique())

# Calculate frequency for each opponent
for opponent in opponents:
    # Filter data for the current opponent
    opponent_data = player_data[player_data['Opponent'] == opponent]
    
    # Calculate frequency for the opponent
    opp_frequency = (
        opponent_data['GW Points']
        .value_counts()
        .sort_index()
        .reset_index(name=f'{opponent}')
    )

    opp_frequency.rename(columns={'index': 'GW Points'}, inplace=True)
    
    # Append to the list
    opponent_frequencies.append(opp_frequency)

# Merge all opponent frequencies into a single DataFrame
counted_data = overall_frequency[['GW Points']]

for freq_df in opponent_frequencies:
    counted_data = counted_data.merge(freq_df, on='GW Points', how='left')

# Fill NaN values with 0 and remove decimals
counted_data.fillna(0, inplace=True)
counted_data = counted_data.astype(int)

# Combine data and reorder columns to place team names in alphabetical order
final_data = overall_frequency.merge(counted_data, on='GW Points')

# Filter and sort players by position and points
def filter_and_sort(data, positions, points_column='GW Points'):
    return data[data['Position'].isin(positions)].sort_values(by=points_column, ascending=False)

def assign_difficulty(data, zscore_column='z_score', position_name=None):
    data = data.copy()
    data['Difficulty'] = pd.qcut(
        data[zscore_column],
        q=5,
        labels=[5, 4, 3, 2, 1],
        duplicates='drop'   # <- important for ties
    )
    data['Difficulty'] = data['Difficulty'].replace(1, 2)
    return data

def process_players(data, positions, position_name):
    # Filter and sort the data based on the specified positions
    filtered = filter_and_sort(data, positions)

    # Compute the z-scores of the original GW Points
    filtered['z_score'] = zscore(filtered['GW Points'])

    # Now aggregate both the z_score and GW Points by Opponent
    z_scores_grouped = (
        filtered.groupby('Opponent', as_index=False)
        .agg({'z_score': 'mean', 'GW Points': 'mean'})
    )

    # Round the z_scores for readability
    #z_scores_grouped['z_score'] = z_scores_grouped['z_score'].round(2)
    z_scores_grouped['Av_GW_Points'] = z_scores_grouped['GW Points'].round(2)
    z_scores_grouped.drop(columns = 'GW Points', inplace= True)

    # Add the Position column
    z_scores_grouped['Position'] = position_name

    # Assign difficulty ratings based on the z-score quantiles
    z_scores_grouped = assign_difficulty(z_scores_grouped, zscore_column='z_score', position_name=position_name)

    return z_scores_grouped


# Process defensive and attacking players
goalkeepers = process_players(player_data, ['GK', 'DEF'], 'GK')
defenders = process_players(player_data, ['GK','DEF'], 'DEF')
midfielders = process_players(player_data, ['MID', 'FWD'], 'MID')
forwards = process_players(player_data, ['MID','FWD'], 'FWD')

# Combined difficulty to assign to player games
FD_points = pd.concat([goalkeepers, defenders, midfielders, forwards])

# Add Team name information
FD_combined = FD_points.sort_values(by = 'Opponent')

# All teams in order 
teams = ['Arsenal', 'Aston Villa', 'Brighton', 'Bournemouth', 'Brentford', 'Burnley',
       'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
       'Leeds', 'Liverpool', 'Man City', 'Man Utd', 'Newcastle',
       'Nottingham Forest', 'Spurs', 'Sunderland', 'West Ham', 'Wolves']

# Create team column
team_col = []

# Loop through teams and add to fixture difficulty sheet 
for team in teams:
    for i in range (1, 9):
        team_col.append(team)

# Create new columns
FD_combined['Team'] = team_col

# Export to csv
FD_combined.to_csv(fr'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\2025_26\Fixtures\Difficulty_ratings\FD_Improved\FD_{gameweek}.csv')