import streamlit as st # type: ignore
import requests # type: ignore
import pandas as pd
import matplotlib as plt # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.patches as patches # type: ignore
from datetime import datetime
import os
import warnings


def run_your_team():

    # Initialize the list in session state if it doesn't exist
    if "team_list" not in st.session_state:
        st.session_state.team_list = []
    
    # Function to add an item to the list
    def add_to_list(item):
        st.session_state.team_list.append(item)

    # Ignore warnings
    warnings.filterwarnings("ignore", category=UserWarning)

    # Get the current week number (1-52)
    current_week = datetime.now().isocalendar()[1]
    event_id = current_week - 34
    GW_team = None
    
    # Ask user for team ID
    team_id = st.text_input("Enter your Team ID:", value=st.session_state.get('chosen_option', ''))

    # Store the team ID in session state for future reference
    if st.button("Save Team ID"):
        st.session_state.chosen_option = team_id
        st.success("Team ID saved!")

    # Provide help tab if user needs
    with st.expander("Click for assistance"):
        st.info('Your ID can be found here when you click on the points tab.')
        st.image('https://github.com/hot-squid/Fantasy-Premier-League/raw/main/Website/Team_ID.jpg')

    
        if team_id:  # Only proceed if team_id is provided
            # Construct the URL for fetching players for the specific teamID and gameweek
            url = f'https://fantasy.premierleague.com/api/entry/{team_id}/event/{event_id}/picks/'

            try:
                # Make the API request
                response = requests.get(url)

                # Check if the request was successful
                response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

                # Get team information 
                team = response.json()
                # Get gameweek picks 
                GW_picks = team['picks']

                # Extract Player ID and Playing Position 
                list_of_players = pd.DataFrame(
                    [(GW_picks[i]['element'], GW_picks[i]['position']) for i in range(len(GW_picks))],
                    columns=['Player ID', 'GW_position']
                )

                # Import accumulated data from latest gameweek
                data = pd.read_csv(r'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/Current_form/Current_Form_M2.csv')

                # Merge list of players with accumulated player data
                GW_team = pd.merge(list_of_players, data, on='Player ID', how='left')

                # file path
                filepath = r'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/main/Website/form.csv'
                # Import form values from the top players
                top_form = pd.read_csv(filepath)

            except requests.exceptions.RequestException as e:
                # Handle request-related errors
                st.error(f'Failed to retrieve data: {e}')
            except Exception as e:
                # Handle other potential errors (like KeyError, ValueError, etc.)
                st.error(f'An error occurred: {e}')

        # Function to draw pitch

        
        def draw_rotated_pitch(ax=None):
            # If no specific axes object is passed, create one
            if ax is None:
                fig, ax = plt.subplots(figsize=(8, 12))

            # Set the pitch background to green
            ax.set_facecolor('#a8df65')  # Light green color

            # Pitch dimensions
            pitch_length = 105
            pitch_width = 68

            # Draw the pitch outline
            plt.plot([0, 0, pitch_width, pitch_width, 0], [0, pitch_length, pitch_length, 0, 0], color="black")

            # Centre circle and centre mark
            centre_circle = plt.Circle((pitch_width / 2, pitch_length / 2), 9.15, color="black", fill=False)
            centre_spot = plt.Circle((pitch_width / 2, pitch_length / 2), 0.2, color="black")
            ax.add_patch(centre_circle)
            ax.add_patch(centre_spot)

            # Halfway line
            plt.plot([0, pitch_width], [pitch_length / 2, pitch_length / 2], color="black")

            # Penalty areas and goal areas
            penalty_area_top = patches.Rectangle((pitch_width / 2 - 16.5, pitch_length - 16.5), 33, 16.5, linewidth=1, edgecolor="black", facecolor="none")
            penalty_area_bottom = patches.Rectangle((pitch_width / 2 - 16.5, 0), 33, 16.5, linewidth=1, edgecolor="black", facecolor="none")
            goal_area_top = patches.Rectangle((pitch_width / 2 - 5.5, pitch_length - 5.5), 11, 5.5, linewidth=1, edgecolor="black", facecolor="none")
            goal_area_bottom = patches.Rectangle((pitch_width / 2 - 5.5, 0), 11, 5.5, linewidth=1, edgecolor="black", facecolor="none")
            ax.add_patch(penalty_area_top)
            ax.add_patch(penalty_area_bottom)
            ax.add_patch(goal_area_top)
            ax.add_patch(goal_area_bottom)

            # Penalty spots
            penalty_spot_top = plt.Circle((pitch_width / 2, pitch_length - 11), 0.2, color="black")
            penalty_spot_bottom = plt.Circle((pitch_width / 2, 11), 0.2, color="black")
            ax.add_patch(penalty_spot_top)
            ax.add_patch(penalty_spot_bottom)

            # Goal boxes
            goal_top = patches.Rectangle((pitch_width / 2 - 3.66, pitch_length), 7.32, 2, linewidth=1, edgecolor="black", facecolor="none")
            goal_bottom = patches.Rectangle((pitch_width / 2 - 3.66, -2), 7.32, 2, linewidth=1, edgecolor="black", facecolor="none")
            ax.add_patch(goal_top)
            ax.add_patch(goal_bottom)

            # Draw the arcs on the penalty areas
            top_arc = patches.Arc((pitch_width / 2, pitch_length - 11), 18.3, 18.3, angle=0, theta1=220, theta2=320, color="black")
            bottom_arc = patches.Arc((pitch_width / 2, 11), 18.3, 18.3, angle=0, theta1=40, theta2=140, color="black")
            ax.add_patch(top_arc)
            ax.add_patch(bottom_arc)

            # Set the axis limits to fit the pitch and turn off axis labels
            ax.set_xlim(-5, pitch_width + 5)
            ax.set_ylim(-5, pitch_length + 5)
            ax.set_xticks([])
            ax.set_yticks([])

            # Set aspect of the plot to be equal to maintain pitch proportions
            ax.set_aspect('equal')

            return ax

        # Function to add team players with data to the pitch
        def add_players(ax, player_positions, first_team_df, top_form):
            
            # Ensure 'Average Form' is numeric
            top_form['Average Form'] = pd.to_numeric(top_form['Average Form'], errors='coerce')

            for i, (x, y) in enumerate(player_positions):
                # Create a marker for the player at the given position
                player_marker = plt.Circle((x, y), 1, color='black', fill=True, edgecolor='black')

                # Ensure the index does not exceed number of players in the team
                if i < len(first_team_df):
                    # Get data to present from dataframe
                    player_name = first_team_df.iloc[i]['Last_Name']
                    player_form = first_team_df.iloc[i]['Form']
                    player_position = first_team_df.iloc[i]['Position']
                    player_cost = first_team_df.iloc[i]['Cost_Today']

                    # Format player cost
                    player_cost_formatted = f"£{player_cost / 10:.1f}M"  # Format to 1 decimal place with £ sign

                    # Add the marker to the plot
                    ax.add_patch(player_marker)

                    # Check against the top_form DataFrame for average form comparison
                    for _, row in top_form.iterrows():
                        
                        if row['Position'] == player_position and row['Average Form'] > player_form and row['Minimum Form'] < player_form:
                            # Add the player's name as a label with a red border if below average
                            ax.text(
                                x, y + 3, f"{player_name}\nForm: {player_form}\nCost: {player_cost_formatted}", ha='center', va='center', 
                                fontsize=7, color='orange',
                                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none')
                            )
                            break

                        elif row['Position'] == player_position and row['Minimum Form'] > player_form and row['Average Form'] > player_form:
                            # Add the player's name as a label with a red border if below average
                            ax.text(
                                x, y + 3, f"{player_name}\nForm: {player_form}\nCost: {player_cost_formatted}", ha='center', va='center', 
                                fontsize=7, color='red',
                                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none')
                            )
                            break
                        
                        else:
                            # If player form is not below average, label without red edge
                            ax.text(
                                x, y + 3, f"{player_name}\nForm: {player_form}\nCost: {player_cost_formatted}", ha='center', va='center', 
                                fontsize=7, color='white',
                                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none')
                        )

    if team_id:
        # If the formation is 3-4-3
        if (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 3) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 4):
            # Define player positions for the 3-4-3 formation
            GK = [(34, 100)]
            DEF = [(55, 82.5), (34, 82.5), (13, 82.5)]
            MID = [(62.5, 55), (43.5, 55), (25, 55), (5, 55)]
            FWD = [(10, 28), (34, 25), (58, 28)]
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # If the formation is 4-4-2
        elif (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 4) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 4):
            # Define player positions for the 4-4-2 formation
            GK = [(34, 100)]
            DEF = [(62.5, 80), (43.5, 80), (25, 80), (5, 80)]  # Left Back, Center Back (Left), Center Back (Right), Right Back
            MID = [(62.5, 55), (43.5, 55), (25, 55), (5, 55)]  # Left Midfielder, Central Midfielders, Right Midfielder
            FWD = [(20, 32), (48, 32)]  # Strikers
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # If the formation is 4-3-3
        elif (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 4) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 3):
            # Define player positions for the 4-3-3 formation
            GK = [(34, 100)]  # Goalkeeper
            DEF = [(62.5, 80), (43.5, 80), (25, 80), (5, 80)]  # Defenders
            MID = [(15, 55), (34, 55), (53, 55)]  # Midfielders
            FWD = [(10, 28), (34, 25), (58, 28)]  # Forwards
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # If the formation is 3-5-2
        elif (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 3) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 5):
            # Define player positions for the 3-5-2 formation
            GK = [(34, 100)]  # Goalkeeper
            DEF = [(55, 82.5), (34, 82.5), (13, 82.5)]  # Defenders (Left, Center, Right)
            MID = [(5, 50), (20, 55), (34, 60), (48, 55), (63, 50)]  # Midfielders
            FWD = [(20, 32), (48, 32)]  # Forwards
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # If the formation is 5-4-1
        elif (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 5) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 4):
            # Define player positions for the 5-4-1 formation
            GK = [(34, 100)]  # Goalkeeper
            DEF = [(5, 72), (20, 80), (34, 80), (48, 80), (63, 72)]  # Defenders (Left to Right)
            MID = [(62.5, 55), (43.5, 55), (25, 55), (5, 55)]  # Midfielders (Left, Center, Right, Advanced)
            FWD = [(34, 32)]  # Forward
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # If the formation is 5-3-2
        elif (GW_team['Position'][0:11].value_counts().get('DEF', 0) == 5) and (GW_team['Position'][0:11].value_counts().get('MID', 0) == 3):
            # Define player positions for the 5-3-2 formation
            GK = [(34, 100)]  # Goalkeeper
            DEF = [(5, 72), (20, 80), (34, 80), (48, 80), (63, 72)]  # Defenders (Left to Right)
            MID = [(15, 55), (34, 55), (53, 55)]  # Midfielders (Left, Center, Right)
            FWD = [(20, 32), (48, 32)]  # Forwards
            SUBS = [(34, 1), (65, 1), (55, 1), (45, 1)]

        # List of all player position coordinates in the team
        player_positions = GK + DEF + MID + FWD + SUBS

        # Export to csv to use in other page
        team = GW_team['Last_Name']

        # Add to session state
        add_to_list(team)

        # Create the rotated green pitch
        fig, ax = plt.subplots(figsize=(8, 12))
        draw_rotated_pitch(ax)

        # Add the players to the pitch
        add_players(ax, player_positions, GW_team, top_form)

        # Post to website
        st.pyplot(fig)

        # Provide help tab if user needs
        with st.expander("Information"):
        
            st.info('''
            
            Your team is compared to the most in-form players by position (GW points scored over past 4 weeks).
                    
            White is good. Orange is okay. Red is poor. 
                    
            Simply take note of the underperformers, their position and price
            and give this information to the transfer scouts in the below tabs''')


