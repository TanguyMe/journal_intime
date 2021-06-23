import streamlit as st

st.title("Online diary")
Pages = ['Utilisateur', 'Coach', 'Sandbox']
page = st.sidebar.radio('Page', Pages)
fonct_clients = ['Ajouter un texte', 'Modifier un texte', 'Lire son texte']

if page == Pages[0]:
    st.header("Utilisateur")
    id_user = st.text_input('Quel est votre ID ?')
    st.write(id_user)
    selec_client = st.radio('Que souhaitez-vous faire ?', fonct_clients)
    st.balloons()
if page == Pages[1]:
    st.write("Coach")
if page == Pages[2]:
    st.button('Hit me')
    st.checkbox('Check me out')
    st.radio('Radio', [1, 2, 3])
    st.selectbox('Select', [1, 2, 3])
    st.multiselect('Multiselect', [1, 2, 3])
    st.slider('Slide me', min_value=0, max_value=10)
    st.select_slider('Slide to select', options=[1, '2'])
    st.text_input('Enter some text')
    st.number_input('Enter a number')
    st.text_area('Area for textual entry')
    st.date_input('Date input')
    st.time_input('Time entry')
    st.file_uploader('File uploader')
    st.color_picker('Pick a color')