import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize variables
chosen_option = None

# Get the current week number (1-52)
current_date = datetime.now().isocalendar()[1]
gameweek = current_date - 35

# Import data at the current gameweek
form_data = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\WIP\Website\.csv_files\Current_Form.csv')

# Define metric types
form = 'Form'

# Create position filters
goalkeepers = form_data['Position'] == 'GK'
defenders = form_data['Position'] == 'DEF'
midfielders = form_data['Position'] == 'MID'
forwards = form_data['Position'] == 'FWD'

# Define a function to get top players by position and metric
def get_performance(position_filter, metric):
    # Determine the number of players to show based on position
    if position_filter.equals(forwards):
        head = 10
    elif position_filter.equals(goalkeepers):
        head = 5
    else:
        head = 15

    # Filter data by position and sort by the given metric
    performance = form_data[position_filter].sort_values(by=metric, ascending=False).head(head)
    return performance

# Get top players by form for each position
gk_form = get_performance(goalkeepers, form)
def_form = get_performance(defenders, form)
mid_form = get_performance(midfielders, form)
fwd_form = get_performance(forwards, form)

# Calculate minimum form of the top players by position
min_gk_form = gk_form[form].min()
min_def_form = def_form[form].min()
min_mid_form = mid_form[form].min()
min_fwd_form = fwd_form[form].min()

# Calculate average form of the top players by position
avg_gk_form = round(gk_form[form].mean(), 3)
avg_def_form = round(def_form[form].mean(), 3)
avg_mid_form = round(mid_form[form].mean(), 3)
avg_fwd_form = round(fwd_form[form].mean(), 3)

# Define the values for each metric
positions = ['GK', 'DEF', 'MID', 'FWD']
avg_form = [avg_gk_form, avg_def_form, avg_mid_form, avg_fwd_form]
min_form = [min_gk_form, min_def_form, min_mid_form, min_fwd_form]

# Create a dictionary with labeled columns
form_data = {
    'Position': positions,
    'Average Form': avg_form,
    'Minimum Form': min_form
}

# Convert the dictionary to a DataFrame
form_df = pd.DataFrame(form_data)

# Export average form for the top players
form_df.to_csv('form.csv')

# Initialize GW_team in session state if it doesn't exist
if 'chosen_option' not in st.session_state:
    st.session_state['chosen_option'] = None  # Default to None to avoid UnboundLocalError

# Sidebar for navigation
with st.sidebar:
    page = st.selectbox("Select a page:", 
                        ["Your Team", "Model_1", 'Model_2', 'FPL_XI', "Info"])

# Page routing based on the selected page
if page == "Your Team":
    from Your_team import run_your_team
    run_your_team()

elif page == "Model_1":
    from Model_1 import run_model_1
    run_model_1()

elif page == 'Model_2':
    from Model_2 import run_model_2
    run_model_2()

elif page == "FPL_XI":
    from Optimum_team import run_differential
    run_differential()

elif page == "Info":
    from Info import run_info
    run_info()