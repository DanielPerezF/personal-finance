import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import plotly.express as px
import utils
import numpy as np
import seaborn as sns

# --- VISUALIZATIONS ---------------------
st.title('Visualizations of spending')
selected = utils.sheet_menu()
gsheet, ncols, currency = utils.get_sheet_and_cols(selected)
st.write('Working in the _{}_ sheet'.format(st.session_state['gsheet']))

if 'auth_state' not in st.session_state: # In case user is not logged in (maybe after exiting and re-entering the app)
    st.warning("Go back to Home page to login")
else:
    authentication_status = st.session_state['auth_state']
    if authentication_status == False:
        st.error('Username or password are incorrect')
    elif authentication_status == None:
        st.warning("Go back to Home page to login")
    elif authentication_status:

        # --- INSIDE APP AFTER LOGIN -------------
        new_data = st.session_state['data'].copy() # Read the data and format dates

        if gsheet == 'inversiones': 
            new_data = utils.process_investments(new_data)
            utils.pie_plot_invs(new_data)
            
        else:  # if personal or doubledeg where date column exists
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
                utils.stacked_bar_chart(monthly_spend, currency, gsheet)

                # --- Heatmap ------------
                utils.get_monthly_heatmap(monthly_spend)
            
            else:
                st.warning('No data matches the filters')

        # --- Sidebar ---------------
        authenticator = st.session_state['authenticator']
        authenticator.logout('Logout', 'sidebar')
