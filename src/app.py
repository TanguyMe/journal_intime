"""Display the streamlit application for the coach and the users"""

import streamlit as st
import requests
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt


def get_data():
    """Return a dataframe containing all the customers' datas"""
    r = requests.get(f'http://127.0.0.1:8000/coach/customers/infos')
    total_col = ['Id', 'Nom', 'Prénom', 'Date de naissance',
                 'Dernier coaching', 'Adresse', 'Mail']
    return pd.DataFrame(r.json(), columns=total_col)


def check_integer(object_to_check):
    """Return whether the given object can be written as an integer or not"""
    # Try to convert the object to an int
    try:
        int(object_to_check)
        return True
    except:
        st.error('Veuillez rentrer un nombre !')
        return False


def check_id(object_to_check: int):
    """Return whether the given object is an existing id from the datas or not"""
    if check_integer(object_to_check):
        # Get the data from the User table
        data = get_data()
        # Check if the given object is a valid id
        cond = int(object_to_check) in data['Id'].values
        if not cond:
            st.error("L'id entré n'est pas valide, réessayez avec un autre id !")
        return cond


def plot_pie(data, title):
    """Given data and title, plot a pie chart"""
    # Extract the values from the dataframe
    labels = data['Emotion'].values
    rates = data['Rate'].values
    # Plot the pie
    plt.pie(rates, autopct="%.1f%%", radius=3, normalize=True)
    plt.title(title)
    # Add a white circle in the center
    my_circle = plt.Circle((0, 0), 1.2, color='white')
    fig = plt.gcf()
    fig.gca().add_artist(my_circle)
    # Add legend
    plt.legend(labels, loc='best')
    plt.axis('equal')
    # Plot
    st.pyplot(fig)
    plt.close()


def add_text(id_user):
    """The user can add a message given his id_user. It works only once a day.
    Otherwise, user should update his message of the day"""
    message_to_add = st.text_input('Quelle est votre ressenti aujourd\'hui ?', max_chars=280)
    # Wait for a message to be entered
    if message_to_add:
        r = requests.post(f'http://127.0.0.1:8000/user/{id_user}/create?message={message_to_add}')
        # Check if the request is successful
        if isinstance(r.json(), str):
            st.warning(r.json())
        else:
            st.success('Votre message a bien été envoyé.')
            st.balloons()


def update_text(id_user):
    """Allow the user to update today's message. If there are no message to update,
     the user should add a new message."""
    r = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read')
    # Extract the date of the most recent message
    most_recent_message = np.sort(np.array(r.json())[:, 3])[-1]
    # Create today date
    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Check if the most recent message date is today
    if most_recent_message >= today:
        r = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read?date={most_recent_message}')
        # Date formatting
        most_recent_message = np.char.replace(most_recent_message, "T", " ")
        st.write(f'Votre message actuel du {most_recent_message} est:')
        # Get the most recent message from the query
        message_recent = r.json()[0][2]
        st.info(message_recent)
        message_to_update = st.text_input('Quelle est votre nouveau message ?', max_chars=280)
        # Wait for a new message
        if message_to_update:
            # Check if the new message is the same as the replaced one
            if message_to_update == message_recent:
                st.warning('Le nouveau message est le même que le précédent. Changez de message !')
            else:
                # Update the message
                requests.put(f'http://127.0.0.1:8000/user/{id_user}/update?message={message_to_update}')
                st.success('Votre message a bien été mis à jour.')
    else:
        st.warning('Il n\'y a pas de message aujourd\'hui. Veuillez en créer un nouveau.')


def read_text(id_user):
    """Display the text for the given date chosen from all the dates where there are messages"""
    r = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read')
    # Get, sort and format all the messages' dates
    dates = np.sort(np.array(r.json())[:, 3])[::-1]
    dates = np.char.replace(dates, "T", " ")
    # Select from the available dates
    date_message = st.selectbox('De quelle date souhaitez-vous voir votre message ?',
                                dates)
    r = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read?date={date_message}')
    # Display the message for the chosen date
    st.write(f'Votre message du {date_message} est: ')
    st.info(r.json()[0][2])


def add_customer():
    """Add a customer. Nom, Prenom and mail are mandatory fields.
    Date_naissance and adresse are optionals"""
    with st.form("Renseignements"):
        # Set range for birth date
        max_date = datetime.datetime.today()
        min_date = datetime.datetime.today()-datetime.timedelta(days=100*365)
        # Acquiring parameters
        prenom = st.text_input('Prénom :', max_chars=55, help='Champ obligatoire')
        nom = st.text_input('Nom :', max_chars=55, help='Champ obligatoire')
        mail = st.text_input('Adresse mail :', max_chars=55, help='Champ obligatoire')
        date_naissance = st.date_input('Date de naissance', min_value=min_date, max_value=max_date)
        date_naissance = datetime.datetime.combine(date_naissance, datetime.time())
        adresse = st.text_input('Adresse :', max_chars=55)
        submitted = st.form_submit_button("Submit")
        # Wait for submit button push
        if submitted:
            # Check if all required parameters are given
            if prenom and nom and mail:
                # Adapt the url string
                url = f'?prenom={prenom}&nom={nom}&mail={mail}'
                if date_naissance:
                    url = url+f'&date_naissance={date_naissance}'
                if adresse:
                    url = url+f'&adresse={adresse}'
                requests.post(f'http://127.0.0.1:8000/coach/create{url}')
                st.success('Votre message a bien été envoyé.')
            else:
                st.warning('Remplissez tous les champs obligatoires svp')


def update_customer():
    """Update a customer information given his id. Prenom, nom, date_naissance, last_coaching date,
     adresse and mail can be changed."""
    id_user = st.text_input('Id du client :', help='Champ obligatoire')
    # Wait for a valid user id
    if id_user and check_id(id_user):
        # Get and display data to update
        data = get_data()
        st.warning('Les informations initiales sont :')
        st.write(data[data['Id'] == int(id_user)])
        with st.form("Renseignements"):
            st.success('Renseignez les nouvelles informations')
            # Set range for birth date
            max_date = datetime.datetime.today()
            min_date = datetime.datetime.today()-datetime.timedelta(days=100*365)
            # Acquiring parameters
            prenom = st.text_input('Prénom :', max_chars=55)
            nom = st.text_input('Nom :', max_chars=55)
            date_naissance = st.date_input('Date de naissance', min_value=min_date, max_value=max_date)
            date_naissance = datetime.datetime.combine(date_naissance, datetime.time())
            last_coaching = st.date_input('Date du dernier coaching', min_value=min_date, max_value=max_date)
            last_coaching = datetime.datetime.combine(last_coaching, datetime.time())
            adresse = st.text_input('Adresse :', max_chars=55)
            mail = st.text_input('Adresse mail :', max_chars=55)
            submitted = st.form_submit_button("Submit")
            # Wait for submit button push
            if submitted:
                # Check if any parameters to update where given
                if prenom or nom or mail or date_naissance or last_coaching or adresse:
                    url = ''
                    # Adapt the request for each new parameter
                    if prenom:
                        url = url + f'prenom={prenom}&'
                    if nom:
                        url = url + f'nom={nom}&'
                    if mail:
                        url = url + f'mail={mail}&'
                    if date_naissance:
                        url = url + f'date_naissance={date_naissance}&'
                    if adresse:
                        url = url+f'adresse={adresse}&'
                    if last_coaching:
                        url = url + f'last_coaching={last_coaching}&'
                    url = url[:-1]
                    requests.put(f'http://127.0.0.1:8000/coach/update/{id_user}?{url}')
                    st.success('Votre message a bien été modifié.')
                else:
                    st.warning('Renseignez au moins un champ à modifier')


def delete_customer():
    """Delete all the customer information given his id"""
    id_user = st.text_input('Id du client :')
    # Wait for a valid user id
    if id_user and check_id(id_user):
        st.error(id_user)
        # Confirmation button
        if st.button(f'Confirmez la suppression de {id_user}'):
            st.info(id_user)
            requests.delete(f'http://127.0.0.1:8000/coach/delete/{id_user}')
            st.success(f'L\'utilisateur {id_user} a bien été supprimé.')


def info_client():
    """Display in a dataframe all the datas from all the customers.
    Filters on id, nom and prenom can be applied."""
    # Get the data from the User table
    data = get_data()
    total_col = ['Id', 'Nom', 'Prénom', 'Date de naissance',
                 'Dernier coaching', 'Adresse', 'Mail']
    # Selecting columns to visualise
    with st.sidebar.beta_expander('Colonnes à visualiser'):
        columns = st.multiselect('Colonnes sélectionnées', options=total_col, default=total_col)
    # Putting filters on the rows to visualise
    with st.sidebar.beta_expander('Filtres'):
        # Id filter
        list_id = st.multiselect('Id sélectionnés', options=data['Id'].unique())
        cond_id = data['Id'].isin(list_id)
        if len(list_id) == 0:
            cond_id = ~cond_id
        # Name filter
        list_nom = st.multiselect('Noms sélectionnés', options=data['Nom'].unique())
        cond_nom = data['Nom'].isin(list_nom)
        if len(list_nom) == 0:
            cond_nom = ~cond_nom
        # Surname filter
        list_prenom = st.multiselect('Prénoms sélectionnés', options=data['Prénom'].unique())
        cond_prenom = data['Prénom'].isin(list_prenom)
        if len(list_prenom) == 0:
            cond_prenom = ~cond_prenom
    # Display dataframe
    st.dataframe(data[cond_id & cond_nom & cond_prenom][columns])


def visu_date():
    """Plot a pie plot from the emotion rate data of a given customer at a given date.
    Display his main feeling and the message of the given day aswell."""
    id_user = st.text_input('Id du client :')
    # Wait for a valid user id
    if id_user and check_id(id_user):
        # Get, sort and format all the messages' dates
        r1 = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read')
        dates = np.sort(np.array(r1.json())[:, 3])[::-1]
        dates = np.char.replace(dates, "T", " ")
        # Select from the valid dates
        date_message = st.selectbox('A quelle date souhaitez-vous voir le message ?',
                                    dates)
        # Get user infos at the given date
        r = requests.get(f'http://127.0.0.1:8000/coach/customers/sentiments/{id_user}/{date_message}')
        # Display the message
        st.write('Message: ')
        st.info(r.json()['Message'][0][0])
        # Display the main emotion
        st.write('Sentiment majoritaire: ')
        st.success(r.json()['Sentiment majoritaire'])
        # Extract the data for the pie plot
        data = pd.DataFrame([[key, value] for key, value in r.json()['Emotions'].items()], columns=['Emotion', 'Rate'])
        # Plot the pie
        plot_pie(data, title='Répartition des émotions')


def visu_periode():
    """Plot a pie plot from the emotions rate data of a given customer on a given period of time."""
    id_user = st.text_input('Id du client :')
    # Wait for a valid user id
    if id_user and check_integer(id_user):
        r1 = requests.get(f'http://127.0.0.1:8000/user/{id_user}/read')
        # Get the min and max message dates for the user
        min_date, max_date = np.sort(np.array(r1.json())[:, 3])[0], np.sort(np.array(r1.json())[:, 3])[-1]
        # Formatting dates
        min_date = datetime.datetime.fromisoformat(str(min_date))
        max_date = datetime.datetime.fromisoformat(str(max_date))
        # Asking for a date range
        periode_date = st.date_input('Sur quelle période souhaitez vous visualiser les émotions',
                                     min_value=min_date, max_value=max_date, value=(min_date, max_date))
        # Waiting for a date range
        if len(periode_date) == 2:
            # Formatting chosen dates
            date_inf = datetime.datetime.combine(periode_date[0], datetime.time())
            date_supp = datetime.datetime.combine((periode_date[1]+datetime.timedelta(days=1)), datetime.time())
            r = requests.get(f'http://127.0.0.1:8000/coach/customers/'
                             f'sentiments/{id_user}?date_inf={date_inf}&date_supp={date_supp}')
            # Check if there is any message on the given period of time
            if len(r.json()) > 0:
                # Get and display data with a pie plot
                data = pd.DataFrame(np.array(r.json()), columns=['Emotion', 'Rate'])
                data.dropna(inplace=True)
                st.write(data)
                plot_pie(data, title='Répartition des émotions')
            else:
                st.error("Il n'y a pas de messages sur la période donnée.")


def visu_globale():
    """Plot 2 pie plots from the emotions rate data of all the customers on a given period of time.
    First one is averaged over all the messages. Second one is averaged on the customers."""
    # Setting up min and max date for messages
    min_date = datetime.datetime(2010, 1, 1, 0, 0, 0)
    max_date = datetime.datetime.today()
    # Asking for a date range
    periode_date = st.date_input('Sur quelle période souhaitez vous visualiser les émotions',
                                 min_value=min_date, max_value=max_date, value=(min_date, max_date))
    # Waiting for a date range
    if len(periode_date) == 2:
        # Formatting chosen dates
        date_inf = datetime.datetime.combine(periode_date[0], datetime.time())
        date_supp = datetime.datetime.combine((periode_date[1]+datetime.timedelta(days=1)), datetime.time())
        r = requests.get(f'http://127.0.0.1:8000/coach/customers/'
                         f'sentiments/global/message/?date_inf={date_inf}&date_supp={date_supp}')
        # Check if there is any message on the given period of time
        if len(r.json()) > 0:
            # Get and display data with a pie plot for each request
            data = pd.DataFrame(np.array(r.json()), columns=['Emotion', 'Rate'])
            data.dropna(inplace=True)
            plot_pie(data, title='Répartition des émotions moyennées sur les messages')
            r = requests.get(f'http://127.0.0.1:8000/coach/customers/'
                             f'sentiments/global/personne/?date_inf={date_inf}&date_supp={date_supp}')
            data = pd.DataFrame(np.array(r.json()), columns=['Emotion', 'Rate'])
            data.dropna(inplace=True)
            plot_pie(data, title='Répartition des émotions moyennées sur les utilisateurs')
        else:
            st.error("Il n'y a pas de messages sur la période donnée")


# Title
st.title("Online diary")
# Options setup
Pages = ['Utilisateur', 'Coach']
page = st.sidebar.radio('Page', Pages)
fonct_clients = ['Ajouter un texte', 'Modifier un texte', 'Lire son texte']
fonct_coach = ['Gestion des informations', 'Visualisation']
fonct_gestion = ['Ajouter', 'Modifier', 'Supprimer']
fonct_visu = ['Infos clients', 'Ressenti à une date', 'Ressenti sur une période', 'Ressenti global']

# Check the chosen page
if page == Pages[0]:
    # User side
    st.header("Utilisateur")
    id_user = st.text_input('Quel est votre ID ?')
    # Wait for valid user id
    if id_user and check_id(id_user):
        # Get the data
        data = get_data()
        # Get the name of the user
        prenom_user = data[data['Id'] == int(id_user)]['Prénom'].values[0]
        st.write(f'Bonjour {prenom_user}, bienvenue dans votre journal en ligne !')
        # Ask for what the user wants to do
        selec_client = st.radio('Que souhaitez-vous faire ?', fonct_clients)
        if selec_client == fonct_clients[0]:
            add_text(id_user)
        if selec_client == fonct_clients[1]:
            update_text(id_user)
        if selec_client == fonct_clients[2]:
            read_text(id_user)
if page == Pages[1]:
    # Coach side
    st.header("Coach")
    # Ask for what the coach wants to do
    selec_coach = st.selectbox('Que souhaitez-vous faire ?', fonct_coach)
    if selec_coach == fonct_coach[0]:
        selec_gestion = st.radio('Choisissez la modification à effectuer: ', fonct_gestion)
        if selec_gestion == fonct_gestion[0]:
            add_customer()
        if selec_gestion == fonct_gestion[1]:
            update_customer()
        if selec_gestion == fonct_gestion[2]:
            delete_customer()
    if selec_coach == fonct_coach[1]:
        selec_visu = st.radio('Que souhaitez-vous faire ?', fonct_visu)
        if selec_visu == fonct_visu[0]:
            info_client()
        if selec_visu == fonct_visu[1]:
            visu_date()
        if selec_visu == fonct_visu[2]:
            visu_periode()
        if selec_visu == fonct_visu[3]:
            visu_globale()
