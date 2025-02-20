import streamlit as st
import pandas as pd
import utils
from streamlit_gsheets import GSheetsConnection
import time

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
        conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
        st.session_state['conn'] = conn # Save connection status to database in session state
        
        if 'data' not in st.session_state: # In case the data was already read before
            utils.read_data('not_other', gsheet=gsheet, ncols=ncols) # Read the data from the selected sheet

        #if st.button('Reload data'): # Manually reading data
        #    if 'data' in st.session_state:
        #        del st.session_state['data']  # Remove old session state data
        #    del st.session_state['conn']
        #    utils.read_data('not_other', gsheet=gsheet, ncols=ncols)
        #    st.success('Data loaded')

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
            data.loc[len(data.index)] = new_row  # Add new row
            st.session_state['data'] = data  # Save the new data to the session state

            st.session_state['conn'].update(data=data, worksheet=st.session_state['gsheet'])  # Update Google Sheets

            # Force reloading data to ensure we see the new row
            #utils.read_data('not_other', gsheet=st.session_state['gsheet'], ncols=len(data.columns))
            st.success(f'New data added to "{st.session_state["gsheet"]}" ☺️')

            #else:
            #    st.error('Incorrect password')

        # --- Sidebar ---------------
        #authenticator = st.session_state['authenticator']
        #authenticator.logout('Logout', 'sidebar')

#st.write(st.session_state['data'].tail(10))