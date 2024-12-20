import streamlit as st
import pandas as pd
import utils
from streamlit_gsheets import GSheetsConnection

# --- ADD NEW TRANSACTIONS --------------------------
st.title('Add new movement')
selected = utils.sheet_menu()
gsheet, ncols, currency = utils.get_sheet_and_cols(selected)
st.write('Working in the _{}_ sheet'.format(st.session_state['gsheet']))

# Add new movements to the session state and database

# --- CHECK AUTHENTICATION --------------------------
# if 'auth_state' not in st.session_state: # Check if user is logged in
#     # st.warning("Go back to Home page to login")
#     authentication_status = True
#     username = 'not_other'
#     st.session_state['auth_state'] = authentication_status
# else:
#     authentication_status = True # st.session_state['auth_state']
#     if authentication_status == False:
#         st.error('Username or password are incorrect')
#     elif authentication_status == None:
#         st.warning("Go back to Home page to login")
#     elif authentication_status:

if 'auth' not in st.session_state:
    inserted_pw = st.number_input('Write the required PIN to insert data', step=1) # Can modify data only with the correct password
    if inserted_pw == int(st.secrets['password']): # Check if password is correct
        st.session_state['auth'] = True
        st.success('Correct password')
    else:
        st.error('Incorrect password')

if 'auth' in st.session_state:
    if st.session_state['auth']:

        # --- INSIDE APP AFTER LOGIN -------------
        if 'data' not in st.session_state: # In case the data was already read before
            conn = st.connection("gsheets", type=GSheetsConnection, ttl=1)
            st.session_state['conn'] = conn # Save connection status to database in session state
            utils.read_data(st.session_state['conn'], 'not_other', gsheet=gsheet, ncols=ncols) # Read the data from the selected sheet

        if st.button('Reload data'): # Manually reading data
            utils.read_data(st.session_state['conn'], 'not_other', gsheet=gsheet, ncols=ncols)
            st.success('Data loaded')

        # --- Input data depending on the selected sheet ---
        new_row = utils.show_input_data(st.session_state['gsheet'])

        # --- Add data ------------------------
        st.subheader('Add new data')
        # inserted_pw = st.number_input('Write the required PIN to insert data', step=1) # Can modify data only with the correct password

        if st.button('Add data'): # Add the transaction to the dataset
            # if st.session_state['username'] == 'other': # If user is 'other' then cant update data
            #     st.error('You are not authorized to update the data')
            # else:
            #if inserted_pw == int(st.secrets['password']): # Check if password is correct
            data = st.session_state['data'].copy()
            data.loc[len(data.index)] = new_row # Add new row to dataframe
            st.session_state['conn'].update(data=data,worksheet = st.session_state['gsheet']) # Update the database
            st.session_state['data'] = data # Update the data in session state
            st.success('New data added to "{}" ☺️'.format(st.session_state['gsheet']))
            #else:
            #    st.error('Incorrect password')

        # --- Sidebar ---------------
        #authenticator = st.session_state['authenticator']
        #authenticator.logout('Logout', 'sidebar')

