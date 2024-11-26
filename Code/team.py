import glob
import os
import pandas as pd

# Folder path where CSV files are stored
folder_path = r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Data\Team\Accumulated\Attacking'  # Change this to the actual folder path

# Use glob to get all CSV files in the folder
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# Dictionary to store DataFrames
dataframes = {}

# Loop through each CSV file and store them in the dictionary
for file in csv_files:
    # Get the file name without the path and extension
    file_name = os.path.splitext(os.path.basename(file))[0]
    
    # Debug: Print the file names being processed
    print(f"Loading file: {file_name}")
    
    # Read the CSV into a DataFrame
    df = pd.read_csv(file)
    
    # Store the DataFrame in the dictionary with the file name as the key
    dataframes[file_name] = df

# Create empty gameweek list
gameweeks = []

# Trim gameweek information to a number
for file in csv_files:
    if len(file) == 92:
        trimmed_file = int(file[87:88])
        gameweeks.append(trimmed_file)
    else:
        trimmed_file = int(file[87:89])
        gameweeks.append(trimmed_file)

gameweeks = sorted(gameweeks)

# Create a new empty list to store selected DataFrames
gameweek_dfs = []

# Loop through each gameweek number
for gw in gameweeks:
    # Construct the key dynamically based on the gameweek number
    gw_key = f'GW_{gw}'
    
    # Debug: Check if the constructed key matches any of the loaded DataFrames
    print(f"Looking for key: {gw_key}")
    
    # Check if the key exists in the dataframes dictionary
    if gw_key in dataframes:
        # Append the DataFrame to the gameweek_dfs list
        gameweek_dfs.append(dataframes[gw_key])
    else:
        print(f"Warning: {gw_key} not found in dataframes")


# Function to de-cumulate the gameweek data 
def decumulate(GW_previous, GW_current):

    # Merge two gameweeks on the right (the most current gameweek)
    merged = pd.merge(GW_previous, GW_current, on='Team',
                      suffixes= ('_GWp', '_GWc'),
                      how='right')

    # List of columns to update by subtracting the previous gameweek values
    columns = ['Playing TimeMP','PerformanceGls','PerformanceAst','ExpectedxG','ExpectedxAG']

    # Create a new DataFrame to store the decumulated values
    decumulated_gw = GW_current.copy()

    # Iterate through each column and calculate the actual gameweek value
    for col in columns:
        # Subtract the previous gameweek values from the current ones, round to 3 decimal places
        decumulated_gw[col] = (merged[f'{col}_GWc'] - merged[f'{col}_GWp'].fillna(0)).round(3)


    # Return the decumulated gameweek data without modifying GW_current
    return decumulated_gw

# Export each individual gameweek to a csv file 
for i in range(1, len(gameweek_dfs)):
    GW = decumulate(gameweek_dfs[i-1], gameweek_dfs[i])
    # Proper f-string formatting for the filename
    GW.to_csv(f'GW_{i + 7}.csv', index=False)