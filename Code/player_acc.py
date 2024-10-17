# Import libraries
import pandas as pd
import warnings
import requests
import os

# URL of the Google Sheet in CSV format
csv_url = "https://docs.google.com/spreadsheets/d/1jh4VynDiD2lNWlaG7caRBCctkuw_uVUCgjWFFaaB9RE/export?format=csv&gid=1381310626"

# Send a request to fetch the CSV
response = requests.get(csv_url)

# Save the file locally
with open('downloaded_sheet.csv', 'wb') as file:
    file.write(response.content)

print("File downloaded successfully.")


df = pd.read_csv('downloaded_sheet.csv', dtype={
    'Player ID': str,
    'Name': str,
    'Last Name': str
})

# Rename columns
df = df.rename(columns={
    'Cost Today.1': 'Cost_Today', 
    'Difficulty Score': 'Diff_Score_5gs',
    'Last Name': 'Last_Name'})

# Create list of columns
columns_to_select = [
    'Player ID', 'Name', 'Last_Name', 'Position', 'Team', 'Cost_Today',
    'Total Points', 'Form', 'Points/Game', 'xGi', 'xGc',             
    'Selection %', 'Goals', 'Assists', 'Clean Sheets', 'GW Points',      
    'Total Bonus Points', 'Total BPS', 'Goals Conceded', 'Minutes',      
    'YC', 'RC', 'Saves', 'Penalties Saved', 'Penalties Missed',          
    'Transfers Out GW', 'Transfers in GW', 'Influence', 'Creativity',   
    'Threat', 'ICT Index'      
]

# Get selected columns from data 
data = df[columns_to_select]

# Work out the current gameweek number
current_gw = df['Last GW'].max()

# Import whole fixture list 
fixtures = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Fixtures.csv')

# Select current gameweek plus next 5 gameweek fixture information
selected_columns = ['Team'] + [f'GW{gw}' for gw in range(current_gw, current_gw + 6)]

# Filter the fixtures to include current + 5 gameeweek information
fixtures = fixtures[selected_columns]

# Merge data with fixture data
Data = data.merge(fixtures, on= 'Team', how= 'left')

# Import fixture difficulty csv
fixture_diff = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Fixtures\Difficulty.csv')

# Create a mapping dictionary from fixture difficulty
mapping = fixture_diff.set_index('Fixture')['Difficulty'].to_dict()

# Replace gameweek fixture information with difficulty score
Data[['CGW', 'NGW', 'NGW2', 'NGW3', 'NGW4', 'NGW5']] = Data.iloc[:, [31, 32, 33, 34, 35, 36]].applymap(mapping.get)

# Calculate accumulated fixture difficulty for up to next 5 gameweeks
for gw in range(1, 6): 
    Data[f'Diff_Score_{gw}_GW'] = Data.iloc[:, 38:38+gw].sum(axis=1)

# List the columns that need to be converted
columns_to_convert = ['Form'] + [f'Diff_Score_{gw}_GW' for gw in range(1, 6)]  # Concatenate 'Form' with generated list

# Convert each column to float
Data[columns_to_convert] = Data[columns_to_convert].astype(float)

# Calculate accumulated FD_index for up to next 5 gameweeks
for i in range(1, 6):
    Data[f'FDI_{i}'] = round(Data.iloc[:, 7] / Data.iloc[:, 43 + i], 4)

# Create a full file path with the current gameweek
file_path = fr'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Players\Accumulated\GW_{current_gw}.csv'

# Export the current working dataset to the specified file path
Data.to_csv(file_path, index=False)

# Delete original file downloaded from google sheets

# Specify the path to the CSV file
file_path = 'downloaded_sheet.csv'

# Check if the file exists
if os.path.exists(file_path):
    os.remove(file_path)
    print(f"{file_path} has been deleted.")
else:
    print("File does not exist.")

