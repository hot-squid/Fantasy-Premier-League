# Import libraries
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
from io import StringIO

# URL to team data
url = 'https://fbref.com/en/comps/9/stats/Premier-League-Stats'

# Function to get attacking team data 
def team_attack(url):

    # Read the URL
    df = pd.read_html(url)[0]

    # Remove multiple indexes within the same header
    df.columns = [''.join(col).strip() for col in df.columns]
    df = df.reset_index(drop=True)

    # Drop non-needed columns
    df.drop(['Unnamed: 1_level_0# Pl', 'Unnamed: 2_level_0Age'], 
    axis=1, inplace=True)

    # Rename columns
    df = df.rename({'Unnamed: 0_level_0Squad' : 'Team', 
                    'Unnamed: 3_level_0Poss': 'Possession'}, axis=1)

    # Return
    return df

# Function to get defensive team data 
def team_defense(url):

    # Read the URL
    df = pd.read_html(url)[1]

    # Remove multiple indexes within the same header
    df.columns = [''.join(col).strip() for col in df.columns]
    df = df.reset_index(drop=True)

    # Drop non-needed columns
    df.drop(['Unnamed: 1_level_0# Pl', 'Unnamed: 2_level_0Age'], 
    axis=1, inplace=True)

    # Rename columns
    df = df.rename({'Unnamed: 0_level_0Squad' : 'Team', 
                    'Unnamed: 3_level_0Poss': 'Possession'}, axis=1)

    # Return
    return df

# Pull current attacking data
attack = team_attack(url)

# Pull current defensive data
defense = team_defense(url)

# Current gameweek
current_gw = attack['Playing TimeMP'].max() - 1

# Create a full file path with the current GW for attack
attack_file_path = fr'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Team\Accumulated\Attacking\GW_{current_gw}.csv'

# Create full file path with current GW for defense
defense_file_path = fr'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Team\Accumulated\Defensive\GW_{current_gw}.csv'

# Export data
attack.to_csv(attack_file_path)
defense.to_csv(defense_file_path)

