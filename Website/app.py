import streamlit as st

import streamlit as st

import streamlit as st

# Set basic page configuration
st.set_page_config(
    page_title="Custom Themed App",
    layout="centered",
    page_icon=None
)

# Enhanced CSS for theme
st.markdown(
    """
    <style>
        /* Global app styling */
        .stApp {
            background-color: #1C1C1C; /* Main app background */
            color: #FFFFFF; /* Main app text color */
            font-family: 'Sans serif', sans-serif; /* Font family */
        }

        /* Primary color elements like buttons */
        .stButton button {
            background-color: #F8F8F8; /* Primary color */
            color: #1C1C1C; /* Text color for buttons */
            border-radius: 8px;
            border: none;
        }
        .stButton button:hover {
            background-color: #1C1C1C; /* Slightly darker hover state */
        }

        /* Headers styling */
        h1, h2, h3, h4, h5, h6 {
            color: #F8F8F8; /* Primary color for headers */
            font-family: 'Sans serif', sans-serif; /* Font family */
        }

        /* Sidebar container styling */
        .css-1d391kg { 
            background-color: #1C1C1C; /* Sidebar background */
            color: #FFFFFF; /* Sidebar text color */
        }
        /* Sidebar expanded content styling (newer Streamlit versions) */
        .css-qbe2hs {
            background-color: #1C1C1C; /* Sidebar background for Streamlit >=1.10 */
            color: #FFFFFF; /* Sidebar text color */
        }

        /* Text input fields */
        .stTextInput > div > div > input {
            background-color: #2C2C2C; /* Input field background */
            color: #E0E0E0; /* Input field text color */
            border: 1px solid #555555; /* Input field border color */
        }

        /* Links */
        a {
            color: #F8F8F8; /* Primary color for links */
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #FFFFFF; /* Scrollbar color */
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555555; /* Scrollbar hover color */
        }
    </style>
    """,
    unsafe_allow_html=True
)
import pandas as pd
from datetime import datetime

# Initialize variables
chosen_option = None

# Get the current week number (1-52)
current_date = datetime.now().isocalendar()[1]
gameweek = current_date - 35

# Import data at the current gameweek
url = 'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.csv'
form_data = pd.read_csv(url)

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
form_df.to_csv('https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/form.csv')

# Initialize GW_team in session state if it doesn't exist
if 'chosen_option' not in st.session_state:
    st.session_state['chosen_option'] = None  # Default to None to avoid UnboundLocalError

# Sidebar for navigation
with st.sidebar:
    page = st.selectbox("Select a page:", 
                        ["Your Team", "The Scout", "Des LynAIm", "Des's Hot Picks", "About"])

# Page routing based on the selected page
if page == "Your Team":
    from Your_team import run_your_team
    run_your_team()

elif page == 'The Scout':
    from Model_2 import run_model_2
    run_model_2()

elif page == "Des LynAIm":
    from Model_2_1 import run_model_2_1
    run_model_2_1()

elif page == "Des's Hot Picks":
    from FPL_XI import run_XI
    run_XI()

elif page == "About":
    from Info import run_info
    run_info()
