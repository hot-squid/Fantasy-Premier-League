import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def run_info():

    # Add logo
    st.image('logo2.webp')

    # Add description
    st.text("""
    FPAL is a Fantasy Premier League Personal Assistant.
            
    The models are built using Linear Optimisation and AI to predict the 
    highest scoring players each week. 
            
    You can read the analysis here:
    https://medium.com/@thomasburnand/which-fpl-player-position-returns-the-most-points-917aa8886ff8
            
    """)

    # Import performance CSV
    performance = pd.read_csv(r'C:\Users\thoma\Code\Projects\Fantasy-Premier-League\Website\Current_Performance\Model_performance.csv')

    # Create dataframe
    df = pd.DataFrame(performance)

    # Initialize the Plotly figure
    fig = go.Figure()

    # Plot lines for each column except 'Gameweek'
    columns_to_plot = ['Model_2.1', 'Model_2', 'FPL_Average']
    for column in columns_to_plot:
        fig.add_trace(go.Scatter(
            x=df['Gameweek'],
            y=df[column],
            mode='lines+markers',
            name=column
        ))

    # Update layout with titles and grid
    fig.update_layout(
        title='Algorithm Performance',
        xaxis_title='Gameweek',
        yaxis_title='Points',
        xaxis=dict(
            tickmode='linear',
            dtick=1
        ),
        legend_title='Metrics',
        template='plotly_white'
    )

    # Show the interactive plot
    st.plotly_chart(fig)

    # Add description
    st.text("""
    These scores reflect the OptimumXI team choice suggested each week. 
    
    The model totals do not include a captain choice (double points), therefore
    more points would be earned above average. 
    """)
