import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection

st.title('Personal finance during double degree')

# USER AUTHENTICATION --------------------
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login','main')

if authentication_status == False:
    st.error('Username or password are incorrect')
elif authentication_status == None:
    st.warning("Please enter your username and password.")
    st.warning("If other use 'other' as  username and 'abc123' as password")
elif authentication_status:

# --- INSIDE APP AFTER LOGIN -------------

    url = st.secrets["public_gsheets_url"]

    with st.spinner("Please wait..."):
        # Read data function
        @st.cache_data(ttl=60*5) #Refresh every 5 minutes
        def read_data(public_url):
            conn = st.experimental_connection("gsheets", type=GSheetsConnection)
            data = conn.read(spreadsheet=public_url)  #, usecols=[0, 1]
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)
            data.astype({'amount':'float'})
            return data

    data = read_data(url)

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)
    
    # --- Sidebar ---------------
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout('Logout', 'sidebar')

    # --- Spending chart ----------
    monthly_spend = data.copy()
    monthly_spend.date = monthly_spend.date.dt.strftime('%Y-%m')
    monthly_spend = pd.pivot_table(monthly_spend, values = 'amount', columns='concept', index='date', aggfunc='sum')
    if st.checkbox('Show monthly data'):
        st.subheader('Montly data')
        st.write(monthly_spend)

    plot = monthly_spend.plot(kind='area')
    plot.set_xlabel('Month')
    plot.set_ylabel('Amount \N{euro sign}')
    plot.set_title('Monthly spending')
    plot.autoscale(enable=True, axis='x', tight=True)

    # move the legend
    plot.legend(title='Concept', bbox_to_anchor=(1, 1.02), loc='upper left', frameon=False)
    st.pyplot(plot.figure, clear_figure=True)
    
    # Heatmap
    def get_monthly_heatmap():
        import plotly.express as px

        fig = px.imshow(monthly_spend, text_auto=True, aspect="auto")
        fig.update_xaxes(side="top")
        st.plotly_chart(fig, theme=None) # , theme="streamlit"
    get_monthly_heatmap()
