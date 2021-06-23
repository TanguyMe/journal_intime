import mysql.connector
import names
from faker import Faker
import datetime
import pandas as pd
import random
from tensorflow import keras


message_to_add = 0
user_to_add = 0


# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)


# Cursor initialization
mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE onlinediary;")

# Remplissage de la table User
prenom_list = ['Alphonse', 'Bernard', 'Claire', 'Didier', 'Eleonore', 'Fabienne',
             'Gerard', 'Hubert', 'Irene', 'Jeanine', 'Kevin', 'Lucien',
             'Michel', 'Nadine', 'Octave', 'Patrick', 'Quentin',
             'Rachel', 'Sylvain', 'Taylor', 'Ulrich']

add_customer = ("INSERT INTO User" 
               "(prenom)"
               "VALUES (%s)")


def add_in_database_several(list_to_add, table, columns):
    add = (f"INSERT INTO {table}" 
               f"({columns})"
               "VALUES (%s)")
    for value in list_to_add:
        try:
            mycursor.execute(add, [value])
        except:
            print(f"{value} est déjà présent dans la base {table}")
    mydb.commit()


def add_in_database(list_to_add, table, columns):
    add = (f"INSERT INTO {table}" 
               f"({columns})"
               f"VALUES {list_to_add}")
    try:
        mycursor.execute(add)
    except:
        print(f"{list_to_add} est déjà présent dans la base {table}")
    mydb.commit()


def generate_user_randomly(nbr_ppl):
    """Add a given number of people generated randomly to the User table"""
    if nbr_ppl > 0 :
        fake = Faker()
        limitbirth = datetime.date.today()-datetime.timedelta(days=18*365)
        columns = 'nom, prenom, date_naissance, mail'
        for i in range(nbr_ppl):
            name = names.get_last_name()
            prenom = names.get_first_name()
            mail = name + '.' + prenom + '@mail.com'
            date_naissance = fake.date_between(start_date='-52y', end_date=limitbirth).isoformat()
            add_in_database((name, prenom, date_naissance, mail), 'User', columns)


generate_user_randomly(user_to_add)


# Remplissage de la table Daily_message

def generate_message(nbr_mess):
    """Add a given number of message from ad dataframe in the Daily_message table
        Also fill the Emotions table with the results from the given message
    """
    if nbr_mess > 0:
        fake = Faker()
        df_data = pd.read_csv('../data/Emotion_Dataworld.csv')
        mycursor.execute("""SELECT id_user FROM User;""")
        list_id_user = mycursor.fetchall()
        columns_mess = 'id_user, text, date_message'
        columns_emotion = 'id_message, nom_emotion, rate_emotion'
        classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
        model = keras.models.load_model('../modelNLP')
        for k in range(nbr_mess):
            id_user = random.choice(list_id_user)[0]
            message = random.choice(df_data['content'].values)
            date_message = fake.date_time_between(start_date='-5y', end_date='now').isoformat()
            date_message = date_message.replace("T", " ")
            add_in_database((id_user, message, date_message), 'Daily_message', columns_mess)
            predictions = model.predict([message])[0]
            mycursor.execute(f"""SELECT id_message
                                FROM Daily_message
                                WHERE id_user = {id_user}
                                AND date_message = '{date_message}';
                            """)
            id_message = mycursor.fetchall()[0][0]
            for j in range(len(classes)):
                rate = predictions[j]
                emotion = classes[j]
                add_in_database((id_message, emotion, rate), 'Emotion', columns_emotion)


generate_message(message_to_add)




