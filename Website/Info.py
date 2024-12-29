import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def run_info():

    # Add logo
    # Add the logo, center it, and make it smaller
    st.markdown(
        """
        <div style="text-align: center;">
            <img src="https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/refs/heads/main/Website/squidward.png" alt="Logo" style="width:75%;"/>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.text("")  # Adds a blank line
    # Add description
    st.text("""
    
    Hot Squid Ink is a freelance data science and machine learning researcher,
    who provides open source analysis. 
            
    The scouts (models) are built using AI and linear optimisation to predict 
    the highest scoring players each week. 
            
    You can read about the analysis here:
    https://medium.com/@hotsquid
    
    Full access to the source code can be found here:
    https://github.com/hot-squid/Fantasy-Premier-League
    """)

    # Import performance CSV
    performance = pd.read_csv(r'https://raw.githubusercontent.com/hot-squid/Fantasy-Premier-League/refs/heads/main/Website/Current_Performance/Model_performance.csv')

    # Create dataframe
    df = pd.DataFrame(performance)

    # Initialize the Plotly figure
    fig = go.Figure()

    # Plot lines for each column except 'Gameweek'
    columns_to_plot = ['Des_LynAIm', 'The_Scout', 'FPL_Average']
    for column in columns_to_plot:
        fig.add_trace(go.Scatter(
            x=df['Gameweek'],
            y=df[column],
            mode='lines+markers',
            name=column
        ))

    # Update layout with titles and grid
    fig.update_layout(
        title='Scout Performance',
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

    st.text("")  # Adds a blank line
    st.text("")  # Adds a blank line

    # Add a title to your Streamlit app
    st.subheader("Buy me a coffee?")

    # Add a description
    st.write("""
    Click the button below to make a secure payment via Stripe.
    """)

    # Add a button that links to the Stripe payment page
    stripe_url = "https://buy.stripe.com/00gbJJ0k03QrbAIfYY"  # Replace with your Stripe payment link
    if st.button("Donate Now"):
        st.markdown(f"[Click here to donate securely via Stripe]({stripe_url})")

