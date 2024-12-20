import streamlit as st
import pandas as pd
import utils
from streamlit_gsheets import GSheetsConnection


# --- VISUALIZATIONS ---------------------
st.title('Visualizations of spending')
selected = utils.sheet_menu()
gsheet, ncols, currency = utils.get_sheet_and_cols(selected)
st.write('Working in the _{}_ sheet'.format(st.session_state['gsheet']))

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

        new_data = st.session_state['data'].copy() # Read the data and format dates

        if gsheet == 'inversiones': 
            new_data = utils.process_investments(new_data)
            utils.pie_plot_invs(new_data)

        else:  # if colombia or italia where date column exists
            new_data['date'] = pd.to_datetime(new_data['date'], yearfirst=True)

            # --- Filter-------
            st.subheader('Filters')

            all_categories = utils.get_categories(st.session_state['gsheet'])
            all_categories.insert(0, 'All') # Add 'All' as the first element

            categories = st.multiselect('Category', all_categories, default='All')
            if 'All' in categories:
                include_categories = all_categories[1:] # Keep all categories except 'All', as it is not an actual category
            else:
                include_categories = categories

            col1, col2 = st.columns(2)
            recurrent = col1.multiselect('Recurrent',[True,False], default=[True,False])
            include = col2.multiselect('Include', [True,False], default=[True])

            min_date = new_data['date'].min()
            max_date = new_data['date'].max()
            left_date = col1.date_input('Minimum date', min_value=min_date, value=min_date)
            right_date = col2.date_input('Maximum date', max_value=max_date, value=max_date, min_value=left_date)
            
            mask = (new_data['category'].isin(include_categories))&(new_data['recurrent'].isin(recurrent))&(new_data['include'].isin(include))&\
                (new_data['date'] >= str(left_date))&(new_data['date'] <= str(right_date))
            new_data['Date'] = pd.to_datetime(new_data.date).dt.strftime('%b-%y')
            filtered_data = new_data[mask]

            # --- Spending chart ----------
            if len(filtered_data)>0: # In case filters don't match any data
                monthly_spend = utils.monthly_table(filtered_data)

                # --- Stacked bar chart -------
                try:
                    utils.stacked_bar_chart(new_data, currency)
                except:
                    st.error('Error generating barchart')

                # --- Heatmap ------------
                try:
                    utils.get_monthly_heatmap(monthly_spend, gsheet)
                except:
                    st.error('Error generating heatmap')
            
            else:
                st.warning('No data matches the filters')

        # --- Sidebar ---------------
        # authenticator = st.session_state['authenticator']
        # authenticator.logout('Logout', 'sidebar')
