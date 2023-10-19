# LIBRARIES ------------------------------
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
from datetime import date

# --- HOME PAGE ------------------------------
st.title('Personal finance during double degree')
st.text('Keep track of personal spending. Add transactions and visualize spending.\nBased on a dataset in GoogleSheets.')
# Allow users to login
# Read and update data
# See monthly spending

# --- USER AUTHENTICATION --------------------
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
elif authentication_status: # Successfull authentication

# --- INSIDE APP AFTER LOGIN -------------

    # url = st.secrets["public_gsheets_url"] # Used if google sheets is public
    conn = st.experimental_connection("gsheets", type=GSheetsConnection, ttl=1)
    st.session_state['conn'] = conn # Save connection status to database in session state

    with st.spinner("Please wait..."):
        # @st.cache_data(ttl=1) #Refresh every n seconds
        def read_data():
            """Read data from Google Sheets dataset into a dataframe and save it in the session state as 'data'"""
            data = conn.read(usecols=list(range(6)), worksheet='doubledeg')
            data['date'] = pd.to_datetime(data['date'], yearfirst=True).dt.strftime('%Y-%m-%d') # Leave as string to avoid bugs of date format changing
            st.session_state['data'] =  data.dropna(how='all') # Remove extra rows that are actually empty

    if 'data' not in st.session_state: # In case the data was already read before
        read_data()
    
    if st.button('Reload data'): # Manually reading data
        read_data()
        st.success('Data loaded')

    # --- MONTHLY SPENDING --------------------------------------
    # See the spending of current and previous month
    st.subheader('Monthly spending')
    col1, col2 = st.columns(2) # For filtering data to show
    recurrent = col1.multiselect('Recurrent',[True,False], default=[True,False])
    include = col2.multiselect('Include', [True,False], default=[True])

    monthly = st.session_state['data'] # Create copy of dataframe
    mask = (monthly['recurrent'].isin(recurrent))&(monthly['include'].isin(include))
    filtered = monthly[mask] # Apply filters
    filtered['date'] = pd.to_datetime(filtered['date'], yearfirst=True)
    
    today_m = date.today().month
    today_y = date.today().year
    this_month = filtered[(filtered.date.dt.month == today_m) & (filtered.date.dt.year == today_y)] # Get only data from current month
    st.write('This month you have spent ' + str(round(this_month['amount'].sum(),1)) + '\N{euro sign}')

    # Chart with total spending for all months
    with st.expander('Monthly spending chart'):  
        filtered = filtered.set_index('date')
        if False in include: # In order to show different colors
            monthly_agg = filtered.groupby([pd.Grouper(freq='M'), 'include'])['amount'].sum().reset_index(1)
            fig = px.bar(monthly_agg, title='Total monthly spending', text_auto='.0f',color='include',
                        labels={'date':'Month', 'value':'Amount \N{euro sign}'})
        else:
            monthly_agg = filtered.groupby(pd.Grouper(freq='M'))['amount'].sum()
            fig = px.bar(monthly_agg, title='Total monthly spending', text_auto='.0f',
                        labels={'date':'Month', 'value':'Amount \N{euro sign}'})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False) # Annotate data
        fig.update_layout(showlegend=False) # Remove legend
        fig.update_xaxes(dtick="M1",tickformat="%b\n%Y") # Show monthly ticks in x-axis
        st.plotly_chart(fig) # Show figure


    # --- SHOW RAW DATA --------------------------------------
    with st.expander('Raw data'):
        # Create copy of data, modify column types and sort to show first most recent transactions
        df = st.session_state['data'].copy().astype({'recurrent':bool,'include':bool}).sort_values(by='date',ascending=False)
        df['date'] = pd.to_datetime(df['date'], yearfirst=True)
        concepts = ['Administrativo','Alojamiento','Celular','Comida U',
                    'Compras varias','Mercado','Salidas','Salud','Transporte','Viajes']
        edited_df = st.data_editor(df, hide_index=True,
                                   column_config={'amount':st.column_config.NumberColumn("Amount", format="\N{euro sign} %.1f"),
                                                  'date':st.column_config.DateColumn('Date'),
                                                  'concept':st.column_config.SelectboxColumn('Concept', help='Type of spending', required = True, options=concepts),
                                                  'recurrent':st.column_config.CheckboxColumn('Recurrent',help='Is it recurrent?',default=True),
                                                  'inclue':st.column_config.CheckboxColumn('Include',help='Include it in monthly averages?',default=True)},
                                    num_rows='dynamic')
        
    if st.button('Update data'): # apply changes made in edited_df and update sessions_state df as well as gsheets database
        with st.status('Updating data'):
            new_df = edited_df.sort_values(by='date',ascending=True) # Return to previous ordering
            new_df['date'] = new_df['date'].dt.strftime('%Y-%m-%d')  # Date column as a string to avoid format changing
            st.session_state['data'] = new_df            # Update the data in session state
            st.session_state['conn'].update(data=new_df) # Update the database
        st.success('Data updated')
            
    # --- SIDEBAR ---------------
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout('Logout', 'sidebar')
