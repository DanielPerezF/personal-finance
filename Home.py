import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
import yaml
from yaml.loader import SafeLoader

st.title('Personal finance during double degree')
st.text('Keep track of personal spending. Add transactions and visualize spending.\nBased on a dataset in GoogleSheets.')

# USER AUTHENTICATION --------------------
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
st.session_state['auth_state'] = authentication_status
st.session_state['authenticator'] = authenticator

if authentication_status == False:
    st.error('Username or password are incorrect')
elif authentication_status == None:
    st.warning("Please enter your username and password.")
    st.warning("If other use 'other' as  username and 'abc123' as password")
elif authentication_status:

# --- INSIDE APP AFTER LOGIN -------------

    # url = st.secrets["public_gsheets_url"]
    conn = st.experimental_connection("gsheets", type=GSheetsConnection, ttl=0)
    st.session_state['conn'] = conn

    with st.spinner("Please wait..."):
        # Read data function
#        @st.cache_data(ttl=30) #Refresh every 30 seconds
        def read_data():
            data = conn.read(usecols=list(range(6)))
            #st.dataframe(data)
            data['date'] = pd.to_datetime(data['date'], yearfirst=True)
            st.session_state['data'] =  data.dropna(how='all')

    read_data()
    if st.button('Reload data'):
        read_data()
        st.success('Data loaded')


    with st.expander('Raw data'):
        df = st.session_state['data'].copy().astype({'recurrent':bool,'include':bool}) #.sort_values(by='date',ascending=False)
        concepts = ['Administrativo','Alojamiento','Celular','Comida U',
                    'Compras varias','Mercado','Salidas','Salud','Transporte','Viajes']
        edited_df = st.data_editor(df, hide_index=True,
                                   column_config={'amount':st.column_config.NumberColumn("Amount", format="\N{euro sign} %.1f"),
                                                  'date':st.column_config.DateColumn('Date'),
                                                  'concept':st.column_config.SelectboxColumn('Concept', help='Type of spending', required = True, options=concepts),
                                                  'recurrent':st.column_config.CheckboxColumn('Recurrent',help='Is it recurrent?',default=True),
                                                  'inclue':st.column_config.CheckboxColumn('Include',help='Include it in monthly averages?',default=True)})
        st.warning('New info is not saved yet')

    # --- Sidebar ---------------
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout('Logout', 'sidebar')
