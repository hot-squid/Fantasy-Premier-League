import pandas as pd
import streamlit as st
import os
from datetime import datetime

def team_analysis():
    # Check if the CSV file exists before attempting to read
    file_path = 'first_team_players.csv'
    
    if os.path.exists(file_path):
        # Read CSV file, skipping the first column
        data = pd.read_csv(file_path, usecols=lambda column: column != 'Unnamed: 0')  # Adjusted to skip the first column by name
        
        # Display the DataFrame in Streamlit
        st.dataframe(data)  

        # Delete the CSV file after displaying
        os.remove(file_path)
        
    else:
        st.warning("The file 'first_team_players.csv' does not exist.")
        return  # Exit if file doesn't exist
