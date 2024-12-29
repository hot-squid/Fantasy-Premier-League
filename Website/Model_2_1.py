import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
import streamlit as st
from datetime import datetime
import os

def run_model_2_1():

    # Get the current week number (1-52)
    current_week = datetime.now().isocalendar()[1]
    event_id = current_week - 35

    # Add the logo, center it, and make it smaller
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/refs/heads/main/Website/Des_Lynam.webp" alt="Logo" style="width:75%;"/>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.text("")  # Adds a blank line
    
    # Provide help tab if user needs
    with st.expander("Information"):
        st.info('''Des LynAIm is the G.O.A.T scout. He uses an improved fixture difficulty rating, in addition to form, to choose players. 
                
                His analysis can be found here:
                https://medium.com/@hotsquid/improved-fixture-difficulty-rating-opponents-to-target-and-avoid-9a38c7f8228b''')

    st.text("")  # Adds a blank line
    st.text("")  # Adds a blank line

    # Ensure 'team_list' is accessed safely
    team_list = st.session_state.get('team_list', [])  # Default to an empty list if not present

    budget = st.slider(
    "What is your budget?",
    min_value=0.0,
    max_value=100.0,
    value=0.1,  # Default value within the range
    format="£%.2fm"  # Floating-point format
    )


    weeks = st.slider(
        "How many weeks are you planning for?",
        min_value=0,
        max_value=5,
        value=1
    )

    # Input positions
    gk = st.text_input("No. of goalkeepers")
    defs = st.text_input("No. of defenders")
    mids = st.text_input("No. of midfielders")
    fwds = st.text_input("No. of forwards")

    # Convert inputs to integers
    try:
        GK = int(gk)
        DEF = int(defs)
        MID = int(mids)
        FWD = int(fwds)
    except ValueError:
        st.error("Please enter valid numbers for player positions.")
        st.stop()


    if GK <= 2 and DEF <= 5 and MID <= 5 and FWD <= 3:
        st.success("Here we go!")

    else:
        st.error("Caution: FPL teams are MAX 2 GKs, 5 DEFs, 5 MIDs and 3 FWDs.'")

    # Define constants
    BUDGET = budget * 10  # Choose your budget (1000 = £100m)
    WEEKS = weeks  # Choose how many weeks you want to prepare for between 1 and 5
    team = st.session_state.team_list
    
    # Create a list of names (from last added team - hopefully the current website user)
    names_to_remove = team[-1].tolist()


    # Run simulation
    if st.button('Run Simulation'):

        # Read csv dataframe
        data = pd.read_csv(r'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.1.csv', index_col=0)

        # Filter `data` to exclude rows with matching names
        data = data[~data['Last_Name'].isin(names_to_remove)]

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
        prob += lpSum(players[i] * prices[i] for i in range(len(data))) >= (BUDGET - 75)

        # Budget constraint: the sum of selected players' prices must be <= BUDGET
        prob += lpSum(players[i] * prices[i] for i in range(len(data))) <= (BUDGET)

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
                    'Current_Price': f"£{prices[index] / 10:.1f}"  # Format with £ and divide by 10
                }
                selected_players.append(player_info)


        # Assuming `selected_players` is a list of dictionaries
        if selected_players:
            # Convert the list to a DataFrame
            selected_players_df = pd.DataFrame(selected_players)

            # Ensure the 'Current_Price' column is cleaned
            if 'Current_Price' in selected_players_df.columns:

                # Display the DataFrame in Streamlit
                st.subheader("Selected Players")
                st.write(selected_players_df)

                # Remove the £ sign and convert to numeric
                selected_players_df['Current_Price'] = selected_players_df['Current_Price'].replace('[£,]', '', regex=True).astype(float)

                # Calculate and display the total cost
                total_cost = selected_players_df['Current_Price'].sum()
                st.write(f"Total Cost: £{total_cost:.1f}")  # Adjusting to one decimal place
            else:
                st.error("Error: 'Current_Price' column is missing in the DataFrame.")
        else:
            st.info("No players selected.")

        # Wildcard button
    # Provide a help tab if the user needs it
    #with st.expander("Wildcard?"):
       # if st.button("Click here only if you plan wildcard"):
          #  st.info('Your team selection has been removed.')
            
            # Check if 'team_list' exists in session state
           # if 'team_list' in st.session_state:
           #     del st.session_state['team_list']  # Clear the 'team_list' from session state
           # else:
            #    st.warning("No team selection found to remove.")

