"""Create the API, run it locally to get the data to run the streamlit app"""

from fastapi import FastAPI
import mysql.connector
from typing import Optional
import datetime
import numpy as np
from fonctions import update_emotions, add_in_database, create_emotion
import os

# print('api cwd: ', os.getcwd())
# print('api file: ', os.path.dirname(__file__))
# print('api path: ', sys.path)
app = FastAPI()

# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)

# Cursor initialization
mycursor = mydb.cursor(buffered=True)

# Use the test database if we are running Pytest, else use the true database
if os.getcwd() == os.path.dirname(__file__) + '/test':
    mycursor.execute("USE testdbdiary;")
else:
    # create_test_db()
    mycursor.execute("Use onlinediary")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/user/{id_user}/read")
async def read_messages(id_user: int, date: Optional[datetime.datetime] = None):
    """Request to get customer infos given a customer id and an optional date.
    Return the request results."""
    # Check if the date is given or not
    if date:
        mycursor.execute(f"""SELECT * FROM Daily_message 
                            WHERE id_user = {id_user}
                            AND date_message = '{date}'""")
    else:
        mycursor.execute(f"""SELECT * FROM Daily_message 
                                WHERE id_user = {id_user}""")
    return mycursor.fetchall()


@app.put("/user/{id_user}/update")
async def update_message(id_user: int, message: str):
    """Replace the current today's message by the new given message for a given id_user.
    Return the customer id and the new message."""
    # Create today datetime at the wanted format
    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    mycursor.execute(f"""UPDATE Daily_message
                        SET text = '{message}'
                        WHERE date_message >= '{today}'
                        AND id_user = {id_user}
""")
    rowcount = mycursor.rowcount
    # Check if the update query applied to a row or not
    if rowcount == 0:
        return 'Il n\'y a pas encore de message aujourd\'hui, vous devez en créer un nouveau.'
    else:
        mydb.commit()
        # Select the id from the updated message
        mycursor.execute(f"""SELECT id_message FROM Daily_message
        WHERE (id_user = {id_user})
        AND (date_message >= '{today}')
        """)
        last_message_id = mycursor.fetchall()[0][0]
        mycursor.execute(f"""SELECT * FROM Emotion
        WHERE id_message = {last_message_id}""")
        # Check if the emotion rate for this message id already exists
        if mycursor.rowcount == 0:
            # Create the emotions if needed
            create_emotion(last_message_id, message)
        else:
            # Update the emotions if it already exists
            update_emotions(last_message_id, message)
        return{'id_user': id_user, 'message': message}


@app.post("/user/{id_user}/create")
def create_message(id_user: int, message: str):
    """Add a given message to the database for a given customer at today's date.
    Fill the emotion table for the given message. Return the customer id and the message"""
    # Create datetime of today at midnight
    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d %H:%M:%S")
    # Query to check if there is already a message for this user today
    mycursor.execute(f"""SELECT id_message
                                FROM Daily_message
                                WHERE date_message >= '{today}'
                                AND id_user = {id_user}
                            """)
    rowcount = mycursor.rowcount
    if rowcount == 1:
        # If there is already a message today, user can't add a new one
        return 'Impossible d\'ajouter ce message. Il y a déjà un message aujourd\'hui, veuillez le modifier.'
    else:
        # Create datetime of today at current time
        date_message = datetime.datetime.today()
        date_message = date_message.strftime("%Y/%m/%d %H:%M:%S")
        columns_mess = 'id_user, text, date_message'
        # Add the message infos to the Daily_message table
        add_in_database((id_user, message, date_message), 'Daily_message', columns_mess)
        mydb.commit()
        # Get the id_message
        mycursor.execute(f"""SELECT id_message
                                    FROM Daily_message
                                    WHERE (id_user = {id_user})
                                    AND (date_message >= '{today}')
                                """)
        infos = mycursor.fetchall()
        id_message = infos[0][0]
        # Fill emotion table for the new message
        create_emotion(id_message, message)
        return {'id_user': id_user, 'message': message}


@app.post("/coach/create")
def create_user(prenom: str, nom: str, mail: str,
                date_naissance: Optional[datetime.datetime] = None, adresse: Optional[str] = None):
    """Prenom, nom and mail are mandatory fields. Date_naissance and adresse are optionals.
    Add a new customer in the database given this parameters."""
    columns = 'nom, prenom, date_naissance, mail, adresse'
    list_to_add = (nom, prenom, date_naissance, mail, adresse)
    add = (f"INSERT INTO User "
           f"({columns}) "
           f"VALUES (%s, %s, %s, %s, %s)")
    mycursor.execute(add, list_to_add)
    mydb.commit()
    return f"L'utilisateur {nom} {prenom} a été créé"


@app.put("/coach/update/{id_user}")
def update_user(id_user: int, prenom: Optional[str] = None, nom: Optional[str] = None, mail: Optional[str] = None,
                date_naissance: Optional[datetime.datetime] = None, adresse: Optional[str] = None,
                last_coaching: Optional[datetime.datetime] = None):
    """Given a user id, replace prenom, nom, mail, date_naissance, adresse and last_coaching date
    in the database if they are given.
    Return a string saying what user and parameters have been updated."""
    update = (prenom, nom, mail, date_naissance, adresse, last_coaching)
    update_columns = ('prenom', 'nom', 'mail', 'date_naissance', 'adresse', 'last_coaching')
    # Prepare an index to select the columns to update
    index = []
    for k in range(len(update)):
        if update[k]:
            index.append(k)
    for k in index:
        # Update all the wanted columns
        update_commande = ("UPDATE User "
                           f"SET {update_columns[k]} = '{update[k]}' "
                           f"WHERE id_user = {id_user}")
        mycursor.execute(update_commande)
        mydb.commit()
    return f"L'utilisateur {id_user} a été modifié pour les paramètres {[update_columns[k] for k in index]}"


@app.delete("/coach/delete/{id_user}")
def delete_user(id_user: int):
    """Delete the user with the given id. Return a string saying which user has been deleted."""
    mycursor.execute(f"""DELETE FROM User
                        WHERE id_user = {id_user}""")
    mydb.commit()
    return f"L'utilisateur {id_user} a été supprimé"


@app.get("/coach/customers/infos")
def list_customers():
    """Return query result to get all the informations from the customers."""
    mycursor.execute(f"""SELECT * FROM User""")
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/{id_user}/{date_message}")
def get_emotion_date(id_user: int, date_message: datetime.datetime):
    """Given a customer id and a date message.
    Return the message, the main feeling and the emotions names and rates."""
    # Query to select the emotion and the rate of a user at a give date
    mycursor.execute(f"""SELECT Emotion.nom_emotion, Emotion.rate_emotion 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message = '{date_message}')
                     """
                     )
    emotions = mycursor.fetchall()
    # Emotion rates
    arr_emotions = np.array(emotions)
    # Main emotion
    sentiment_maj = arr_emotions[np.argmax(arr_emotions[:, 1])][0]
    # Query to select the message corresponding to the id and the date
    mycursor.execute(f"""SELECT Daily_message.text 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message = '{date_message}')"""
                     )
    message = mycursor.fetchall()
    return {'Message': message, 'Sentiment majoritaire': sentiment_maj, 'Emotions': arr_emotions}


@app.get("/coach/customers/sentiments/{id_user}")
def get_emotion_range(id_user: int, date_inf: datetime.datetime, date_supp: datetime.datetime):
    """Given a customer id and two dates,
    return the results of the average emotions for the given period of time."""
    mycursor.execute(f"""SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message > '{date_inf}'
                     AND Daily_message.date_message < '{date_supp}') 
                     GROUP BY Emotion.nom_emotion"""
                     )
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/global/message/")
def get_emotion_global_message(date_inf: datetime.datetime, date_supp: datetime.datetime):
    """Given a customer two dates,
    return the results of emotions rates averaged on messages for the given period of time."""
    mycursor.execute(f"""SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (Daily_message.date_message > '{date_inf}'
                     AND Daily_message.date_message < '{date_supp}') 
                     GROUP BY Emotion.nom_emotion"""
                     )
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/global/personne/")
def get_emotion_global_personne(date_inf: datetime.datetime, date_supp: datetime.datetime):
    """Given a customer two dates,
    return the results of emotions rates averaged on customers for the given period of time."""
    mycursor.execute(f"""SELECT nom_emotion, AVG(rate) FROM (
    SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) as rate,
    User.id_user FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user
    LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message WHERE (Daily_message.date_message > '{date_inf} '
    AND Daily_message.date_message < '{date_supp}]')  GROUP BY User.id_user, Emotion.nom_emotion
    )
    AS t GROUP BY nom_emotion;"""
                     )
    return mycursor.fetchall()


@app.delete("/coach/delete/message/{id_message}")
def delete_message(id_message: int):
    """Delete the message with the given id. Return a string saying which message has been deleted."""
    mycursor.execute(f"""DELETE FROM Daily_message
                        WHERE id_message = {id_message}""")
    mydb.commit()
    return f"Le message {id_message} a été supprimé"
