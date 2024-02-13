import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px

# --- VISUALIZATIONS ---------------------
st.title('Visualizations of spending')
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
        new_data = st.session_state['data'].copy() # Read the data
        new_data['date'] = pd.to_datetime(new_data['date'], yearfirst=True)

        # --- Filter-------
        st.subheader('Filters')

        all_categories = ['All','Administrativo','Alojamiento','Celular','Comida U','Compras varias',
                        'Mercado','Salidas','Salud','Transporte','Viajes']
        
        categories = st.multiselect('Category', all_categories, default='All')
        if 'All' in categories:
            include_categories = all_categories[1:]
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
            monthly_spend = pd.pivot_table(filtered_data, values = 'amount', columns='category', index='Date', aggfunc='sum', sort=False)
            monthly_spend = monthly_spend[['Alojamiento','Viajes','Mercado','Administrativo','Salidas',
                                        'Celular','Comida U','Compras varias','Salud','Transporte']]    # Reorder columns
            with st.expander('Show monthly data'):
                st.subheader('Montly data')
                total_monthly_spend = monthly_spend.copy()
                total_monthly_spend['Total'] = total_monthly_spend.sum(axis=1)
                labels = all_categories  # Get the names for all categories
                labels[0] = 'Total'    # Replace the first to show instead of 'All' as 'Total'
                st.dataframe(total_monthly_spend[labels].iloc[::-1]) # See the table with total monthly spending for each category, most recent first

            # --- Stacked area chart -------
            plt.style.use("dark_background")
            plot = monthly_spend.plot(kind='area', colormap='Paired')
            plot.set_xlabel('Date')
            plot.set_ylabel('Amount \N{euro sign}')
            plot.set_title('Monthly spending')
            plot.autoscale(enable=True, axis='x', tight=True)

            # move the legend
            handles, labels = plot.get_legend_handles_labels()
            plot.legend(reversed(handles), reversed(labels), title='Category', bbox_to_anchor=(1, 1.02),
                        loc='upper left', frameon=False, title_fontproperties={'weight':"bold", 'size':'large'})
            st.pyplot(plot.figure, clear_figure=True)
            st.text('\n')       # Add extra space

            # --- Heatmap ------------
            def get_monthly_heatmap(df):
                fig = px.imshow(df, text_auto=True, aspect="auto")
                fig.update_xaxes(side="top")
                st.plotly_chart(fig, theme=None) # , theme="streamlit"
            get_monthly_heatmap(monthly_spend)
        
        else:
            st.warning('No data matches the filters')

        # --- Sidebar ---------------
        authenticator = st.session_state['authenticator']
        authenticator.logout('Logout', 'sidebar')
