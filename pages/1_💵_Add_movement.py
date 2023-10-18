import streamlit as st
import pandas as pd

st.title('Add new transaction')
if 'auth_state' not in st.session_state:
    st.warning("Go back to Home page to login")
else:
    authentication_status = st.session_state['auth_state']
    if authentication_status == False:
        st.error('Username or password are incorrect')
    elif authentication_status == None:
        st.warning("Go back to Home page to login")
    elif authentication_status:

        # --- INSIDE APP AFTER LOGIN -------------

        # --- Input data ---
        col1, col2 = st.columns(2)
        date = col1.date_input('Date').strftime("%Y-%m-%d")
        amount = col2.number_input('Amount')
        concept = st.selectbox('Concept', ['Administrativo','Alojamiento','Celular','Comida U','Compras varias',
                                        'Mercado','Salidas','Salud','Transporte','Viajes'])
        description = st.text_input('Description')
        col1, col2 = st.columns(2)
        recurrent = col1.checkbox('Recurrent spending', value=True)
        include = col2.checkbox('Include', value=True)

        # --- Add data ---
        st.subheader('Add new data')
        new_row = [date,amount,concept,description,recurrent,include]
        inserted_pw = st.number_input('Write the required PIN to insert data', step=1)

        if st.button('Add data'):
            if inserted_pw == int(st.secrets['password']):
                data = st.session_state['data'].copy()
                st.write(data.dtypes)
                data.loc[len(data.index)] = new_row
                st.session_state['conn'].update(data=data) # Update the database
                st.session_state['data'] = data
                st.success('New data added ☺️')
            else:
                st.error('Incorrect password')

        # --- Sidebar ---------------
        authenticator = st.session_state['authenticator']
        authenticator.logout('Logout', 'sidebar')

