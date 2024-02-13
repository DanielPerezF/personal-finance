# LIBRARIES ------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import yaml
from yaml.loader import SafeLoader
from datetime import date

# --- HOME PAGE ------------------------------
st.title('Personal finance app')
st.text('Keep track of personal spending. Add transactions and visualize spending.\nBased on a private dataset in GoogleSheets.')
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

name, authentication_status, username = authenticator.login()
st.session_state['auth_state'] = authentication_status
st.session_state['authenticator'] = authenticator
st.session_state['username'] = username

if authentication_status == False:
    st.error('Username or password are incorrect')
elif authentication_status == None:
    st.warning("Please enter your username and password.")
    st.warning("If other use 'other' as  username and 'abc123' as password to generate randomize data.")
elif authentication_status: # Successfull authentication

# --- INSIDE APP AFTER LOGIN -------------

    # --- READ DATA FROM GOOGLE SHEETS ---------------------
    # url = st.secrets["public_gsheets_url"] # Used if google sheets is public
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=1)
    st.session_state['conn'] = conn # Save connection status to database in session state

    with st.spinner("Please wait..."):
        # @st.cache_data(ttl=1) #Refresh every n seconds
        def read_data(gsheet='doubledeg', ncols=6):
            """Read data from Google Sheets dataset into a dataframe and save it in the session state as 'data'"""
            data = conn.read(usecols=list(range(ncols)), worksheet=gsheet)
            if gsheet == 'inversiones':
                data['Opening date'] = pd.to_datetime(data['Opening date'], yearfirst=True).dt.strftime('%Y-%m-%d') # Leave as string to avoid bugs of date format changing
                data['Closing date'] = pd.to_datetime(data['Closing date'], yearfirst=True).dt.strftime('%Y-%m-%d') # Leave as string to avoid bugs of date format changing
            else:
                data['date'] = pd.to_datetime(data['date'], yearfirst=True).dt.strftime('%Y-%m-%d') # Leave as string to avoid bugs of date format changing
            
            if username == 'other':
                data['amount'] = data['amount']*np.random.rand(len(data)) # Randomize amount for 'other' user
                data.drop(columns=['description'], inplace=True) # Remove description column for 'other' user
            st.session_state['data'] =  data.dropna(how='all') # Remove extra rows that are actually empty

    # --- CHOOSE OPTION ------------------------------
    def get_sheet_and_cols(selection):
        if selection=='Italy':
            gsheet = 'doubledeg'
            ncols = 6
            currency = '\N{euro sign}'
        elif selection=='Colombia':
            gsheet = 'personal'
            ncols = 6
            currency = '$'
        elif selection=='Investments':
            gsheet = 'inversiones'
            ncols = 8
            currency = '$'
        return gsheet, ncols, currency
    
    def on_change(key):
        selection = st.session_state[key]
        gsheet, ncols, _ = get_sheet_and_cols(selection)
        st.session_state['gsheet'] = gsheet
        read_data(gsheet, ncols)

    selected = option_menu(
        menu_title=None,
        options=['Italy','Colombia','Investments'],
        icons=['airplane','house','cash'],
        default_index=0,
        menu_icon='cast',
        orientation='horizontal',
        key='menu_1',
        on_change=on_change
    )
    gsheet, ncols, currency = get_sheet_and_cols(selected)

    if 'data' not in st.session_state: # In case the data was already read before
        read_data(gsheet, ncols) # Read the data from the selected sheet
    
    if st.button('Reload data'): # Manually reading data
        read_data(gsheet, ncols)
        st.success('Data loaded')

    # --- MONTHLY SPENDING --------------------------------------
    # See the spending of current and previous month
    st.subheader('Monthly spending')
    if username == 'other':
        st.text('For user "other" the data is randomized')

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
    this_month_sum = this_month['amount'].sum()  # Total amount spent this month
    st.write('This month you have spent ' +currency + '{:,.0f}'.format(this_month_sum))

    # Chart with total spending for all months
    with st.expander('Monthly spending chart'):  
        filtered = filtered.set_index('date')
        if False in include: # In order to show different colors
            monthly_agg = filtered.groupby([pd.Grouper(freq='M'), 'include'])['amount'].sum().reset_index(1)
            fig = px.bar(monthly_agg, title='Total monthly spending', text_auto='.0f',color='include',
                        labels={'date':'Month', 'value':f'Amount {currency}'})
        else:
            monthly_agg = filtered.groupby(pd.Grouper(freq='M'))['amount'].sum()
            monthly_agg.index = monthly_agg.index.strftime("%Y-%m")
            fig = px.bar(monthly_agg, title='Total monthly spending', text_auto='.0f',
                        labels={'date':'Month', 'value':f'Amount {currency}'})
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False) # Annotate data
        fig.update_layout(showlegend=False) # Remove legend
        fig.update_xaxes(dtick="M1",tickformat="%b\n%Y") # Show monthly ticks in x-axis
        st.plotly_chart(fig) # Show figure


    # --- SHOW RAW DATA --------------------------------------
    with st.expander('Raw data'):
        # Create copy of data, modify column types and sort to show first most recent transactions
        df = st.session_state['data'].copy().astype({'recurrent':bool,'include':bool}).sort_values(by='date',ascending=False)
        df['date'] = pd.to_datetime(df['date'], yearfirst=True)
        categories = ['Administrativo','Alojamiento','Celular','Comida U',
                    'Compras varias','Mercado','Salidas','Salud','Transporte','Viajes']
        edited_df = st.data_editor(df, hide_index=True,
                                   column_config={'amount':st.column_config.NumberColumn("Amount", format=f"{currency} %.1f"),
                                                  'date':st.column_config.DateColumn('Date'),
                                                  'category':st.column_config.SelectboxColumn('Category', help='Type of spending', required = True, options=categories),
                                                  'recurrent':st.column_config.CheckboxColumn('Recurrent',help='Is it recurrent?',default=True),
                                                  'inclue':st.column_config.CheckboxColumn('Include',help='Include it in monthly averages?',default=True)},
                                    num_rows='dynamic')
        
    if st.button('Update data'): # apply changes made in edited_df and update sessions_state df as well as gsheets database
        if username=='other':
            st.error('You are not authorized to update the data')
        else:
            with st.status('Updating data'):
                new_df = edited_df.sort_values(by='date',ascending=True) # Return to previous ordering
                new_df['date'] = new_df['date'].dt.strftime('%Y-%m-%d')  # Date column as a string to avoid format changing
                st.session_state['data'] = new_df            # Update the data in session state
                st.session_state['conn'].update(data=new_df, worksheet=st.session_state['gsheet']) # Update the database
            st.success('Data updated')
            
    # --- SIDEBAR ---------------
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout('Logout', 'sidebar')
