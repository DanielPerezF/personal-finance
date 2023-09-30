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

    with st.spinner("Please wait..."):
        # Read data function
        @st.cache_data(ttl=60*5) #Refresh every 5 minutes
        def read_data():
            conn = st.experimental_connection("gsheets", type=GSheetsConnection)
            st.session_state['conn'] = conn
            data = conn.read(usecols=list(range(6)))
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)
            return data.dropna(how='all')

    st.session_state['data'] = read_data()
    reload = st.button('Reload data')
    if reload:
        st.session_state['data'] = read_data()

    with st.expander('Raw data'):
        st.write('Data')
        st.dataframe(st.session_state['data'])
    
    # --- Sidebar ---------------
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout('Logout', 'sidebar')
