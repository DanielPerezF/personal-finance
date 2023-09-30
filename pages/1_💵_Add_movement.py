import streamlit as st
import pandas as pd

st.title('Add new transaction')

authentication_status = st.session_state['auth_state']

if authentication_status == False:
    st.error('Username or password are incorrect')
elif authentication_status == None:
    st.warning("Go back to Home page to login")
elif authentication_status:

    # --- INSIDE APP AFTER LOGIN -------------

    # --- Input data ---
    date = st.date_input('Date').strftime("%d-%m-%Y")
    amount = st.number_input('Amount', step = 1)
    concept = st.selectbox('Concept', ['Administrativo','Alojamiento','Celular','Comida U','Compras varias',
                                    'Mercado','Salidas','Salud','Transporte','Viajes'])
    description = st.text_input('Description')
    recurrent = st.checkbox('Recurrent spending', value=True)
    include = st.checkbox('Include', value=True)

    # --- Add data ---
    st.subheader('Add new data')
    new_row = [date,amount,concept,description,recurrent,include]
    inserted_pw = st.text_input('Write the password to insert data')

    data = st.session_state['data']

    if st.button('Add data'):
        if inserted_pw == st.secrets['password']:
            data.loc[len(data.index)] = new_row
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)
            st.session_state['conn'].update(data=data)
            st.success('New data added ☺️')
        else:
            st.error('Incorrect password')

    st.session_state['data'] = data
    # --- Sidebar ---------------
    authenticator = st.session_state['authenticator']
    authenticator.logout('Logout', 'sidebar')

