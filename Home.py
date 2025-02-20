# LIBRARIES ------------------------------
import streamlit as st
# import streamlit_authenticator as stauth
from streamlit_gsheets import GSheetsConnection
from streamlit_option_menu import option_menu
import yaml
from yaml.loader import SafeLoader
import utils

# --- HOME PAGE ------------------------------
st.set_page_config(layout="wide")
st.title('Personal finance app')
st.text('Keep track of personal spending. Add transactions and visualize spending.\nBased on a private dataset in GoogleSheets.')
# Allow users to login
# Read and update data
# See monthly spending

# --- USER AUTHENTICATION --------------------
# with open('config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# authenticator = stauth.Authenticate(
#     config['credentials'],
#     config['cookie']['name'],
#     config['cookie']['key'],
#     config['cookie']['expiry_days'],
#     config['preauthorized']
# )

# name, authentication_status, username = authenticator.login()
# st.session_state['auth_state'] = authentication_status
# st.session_state['authenticator'] = authenticator


# if authentication_status == False:
#     st.error('Username or password are incorrect')
# elif authentication_status == None:
#     st.warning("Please enter your username and password.")
#     st.warning("If other use 'other' as  username and 'abc123' as password to generate randomize data.")
# elif authentication_status: # Successfull authentication

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

        # --- READ DATA FROM GOOGLE SHEETS ---------------------
        # url = st.secrets["public_gsheets_url"] # Used if google sheets is public
        conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
        st.session_state['conn'] = conn # Save connection status to database in session state

        # --- CHOOSE OPTION ------------------------------
        # if username == 'Lupi':
        #     selected = 'juanis'
        selected = utils.sheet_menu()
        gsheet, ncols, currency = utils.get_sheet_and_cols(selected)

        if 'data' not in st.session_state: # In case the data was already read before
            utils.read_data('not_other', gsheet=gsheet, ncols=ncols) # Read the data from the selected sheet
        # utils.read_data('not_other', gsheet=gsheet, ncols=ncols) # Read the data from the selected sheet

        #if st.button('Reload data'): # Manually reading data
        #    if 'data' in st.session_state:
        #        del st.session_state['data']  # Remove old session state data
        #    del st.session_state['conn']
        #    utils.read_data('not_other', gsheet=gsheet, ncols=ncols)
        #    st.success('Data loaded')

        #st.write(st.session_state['data'].tail(10))

        # --- MONTHLY SPENDING --------------------------------------
        # See the spending of current and previous month
        st.subheader('Monthly spending')
        # if username == 'other':
        #     st.text('For user "other" the data is randomized')

        col1, col2 = st.columns(2) # For filtering data to show
        recurrent = col1.multiselect('Recurrent',[True,False], default=[True,False])
        include = col2.multiselect('Include', [True,False], default=[True])

        filtered = utils.monthly_total_spending(st.session_state['data'], currency, recurrent, include)

        # Chart with total spending for all months
        if filtered is not None:  # filtered is None if there using ghseet "inversiones" -> no need for monthly plot
            with st.expander('Monthly spending chart'):  
                utils.monthly_spending_plot(filtered,include,currency)


        # --- SHOW RAW DATA --------------------------------------
        with st.expander('Raw data'):
            # Create copy of data, modify column types and sort to show first most recent transactions
            edited_df = utils.show_raw_data(st.session_state['data'], st.session_state['gsheet'], currency)
            
        if st.button('Update data'): # apply changes made in edited_df and update sessions_state df as well as gsheets database
            # if username=='other':
            #     st.error('You are not authorized to update the data')
            # else:
            with st.status('Updating data'):
                utils.update_data(edited_df, st.session_state['gsheet'])
            st.success('Data updated')
                
        # --- SIDEBAR ---------------
        # st.sidebar.title(f'Welcome {username}!')
        # authenticator.logout('Logout', 'sidebar')
