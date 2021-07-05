"""Script to fill the database with randomised values
Enter how many messages and user you want to add in the parameters below"""

import mysql.connector
import names
from faker import Faker
import datetime
import pandas as pd
import random
from tensorflow import keras

# Number of messages to add
message_to_add = 0
# Number of users to add
user_to_add = 0


# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)


# Cursor initialization
mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE onlinediary;")


def add_in_database(list_to_add, table, columns):
    """Add a list of elements in the database given a list of elements to add, a table and the table columns to add."""
    add = (f"INSERT INTO {table}" 
           f"({columns})"
           f"VALUES {list_to_add}")
    # Try to execute the query to add the given list to the columns' table
    try:
        mycursor.execute(add)
    # If it doesn't work, print that the list is already existing in the table
    except:
        print(f"{list_to_add} est déjà présent dans la base {table}")
    mydb.commit()


def generate_user_randomly(nbr_ppl):
    """Add a given number of people generated randomly to the User table"""
    if nbr_ppl > 0:
        # Initialise random generator
        fake = Faker()
        # Set limitbirth to 18 years before today
        limitbirth = datetime.date.today()-datetime.timedelta(days=18*365)
        # Columns to add
        columns = 'nom, prenom, date_naissance, mail'
        for i in range(nbr_ppl):
            # Generates random name, surname, mail and date of birth
            name = names.get_last_name()
            prenom = names.get_first_name()
            mail = name + '.' + prenom + '@mail.com'
            date_naissance = fake.date_between(start_date='-52y', end_date=limitbirth).isoformat()
            # Add the generated informations in the User table
            add_in_database((name, prenom, date_naissance, mail), 'User', columns)


def generate_message(nbr_mess):
    """Add a given number of message from ad dataframe in the Daily_message table
        Also fill the Emotions table with the results from the given message
    """
    if nbr_mess > 0:
        # Initialise random generator
        fake = Faker()
        # Import the text samples
        df_data = pd.read_csv('../data/Emotion_Dataworld.csv')
        # Get all the existing customer ids
        mycursor.execute("""SELECT id_user FROM User;""")
        list_id_user = mycursor.fetchall()
        columns_mess = 'id_user, text, date_message'
        columns_emotion = 'id_message, nom_emotion, rate_emotion'
        classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
        # Immport model to predict emotion rates
        model = keras.models.load_model('../modelNLP')
        for k in range(nbr_mess):
            # Select a random user id and a random message, create a random date
            id_user = random.choice(list_id_user)[0]
            message = random.choice(df_data['content'].values)
            date_message = fake.date_time_between(start_date='-5y', end_date='now').isoformat()
            date_message = date_message.replace("T", " ")
            # Add the informations in the Daily_message table
            add_in_database((id_user, message, date_message), 'Daily_message', columns_mess)
            # Make predictions
            predictions = model.predict([message])[0]
            # Select the id of the most recent message
            mycursor.execute(f"""SELECT id_message
                                FROM Daily_message
                                WHERE id_user = {id_user}
                                AND date_message = '{date_message}';
                            """)
            id_message = mycursor.fetchall()[0][0]
            for j in range(len(classes)):
                # Add each emotion rate on the emotion table
                rate = predictions[j]
                emotion = classes[j]
                add_in_database((id_message, emotion, rate), 'Emotion', columns_emotion)


# Remplissage de la table User
generate_user_randomly(user_to_add)
# Remplissage de la table Daily_message et Emotion
generate_message(message_to_add)
