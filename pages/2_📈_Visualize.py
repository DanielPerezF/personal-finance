import streamlit as st
import pandas as pd

# ------------------------
st.title('Visualizations of spending')

authentication_status = st.session_state['auth_state']

if authentication_status == False:
    st.error('Username or password are incorrect')
elif authentication_status == None:
    st.warning("Go back to Home page to login")
elif authentication_status:

    # --- INSIDE APP AFTER LOGIN -------------

    # --- Spending chart ----------
    monthly_spend = st.session_state['data'].copy()
    monthly_spend.date = monthly_spend.date.dt.strftime('%Y-%m')
    monthly_spend = pd.pivot_table(monthly_spend, values = 'amount', columns='concept', index='date', aggfunc='sum')
    with st.expander('Show monthly data'):
        st.subheader('Montly data')
        st.dataframe(monthly_spend)

    plot = monthly_spend.plot(kind='area')
    plot.set_xlabel('Month')
    plot.set_ylabel('Amount \N{euro sign}')
    plot.set_title('Monthly spending')
    plot.autoscale(enable=True, axis='x', tight=True)

    # move the legend
    plot.legend(title='Concept', bbox_to_anchor=(1, 1.02), loc='upper left', frameon=False)
    st.pyplot(plot.figure, clear_figure=True)

    # Heatmap
    def get_monthly_heatmap():
        import plotly.express as px

        fig = px.imshow(monthly_spend, text_auto=True, aspect="auto")
        fig.update_xaxes(side="top")
        st.plotly_chart(fig, theme=None) # , theme="streamlit"
    get_monthly_heatmap()

    # --- Sidebar ---------------
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar')
