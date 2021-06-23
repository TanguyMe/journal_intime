from fastapi import FastAPI, Form
import mysql.connector
from typing import Optional
import datetime
import numpy as np
from fonctions import update_emotions, add_in_database, create_emotion
# from tensorflow import keras
#
# print("Salut")
# model = keras.models.load_model('../modelNLP', compile=True)
# print("Au revoir")
# print(model.predict(['essai de phrase à prédire'])[0])

app = FastAPI()

# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)

# Cursor initialization
mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE onlinediary;")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/user/{id_user}/read")
async def read_messages(id_user: int, date: Optional[datetime.datetime] = None):
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
    today = datetime.datetime.today()
    today = today.strftime("%Y/%m/%d %H:%M:%S")
    mycursor.execute(f"""SELECT id_message FROM Daily_message
    WHERE id_user = {id_user}
    ORDER BY date_message DESC
    """)
    last_message_id = mycursor.fetchall()[0][0]
    mycursor.execute(f"""UPDATE Daily_message
                        SET text = '{message}'
                        WHERE id_message = {last_message_id}
""")
    mydb.commit()
    update_emotions(last_message_id, message)
    return{'id_user': id_user, 'message': message}


@app.post("/user/{id_user}/create")
def create_message(id_user: int, message: str):
    date_message = datetime.datetime.today()
    date_message = date_message.strftime("%Y/%m/%d %H:%M:%S")
    columns_mess = 'id_user, text, date_message'
    add_in_database((id_user, message, date_message), 'Daily_message', columns_mess)
    mycursor.execute(f"""SELECT id_message
                                FROM Daily_message
                                WHERE id_user = {id_user}
                                ORDER BY date_message DESC;
                            """)
    id_message = mycursor.fetchall()[0][0]
    create_emotion(id_message, message)
    return {'id_user': id_user, 'message': message}


@app.post("/coach/create")
def create_user(prenom: str, name: str, mail: str,
                date_naissance: Optional[datetime.datetime] = None, adresse: Optional[str] = None):
    columns = 'nom, prenom, date_naissance, mail, adresse'
    list_to_add = (name, prenom, date_naissance, mail, adresse)
    add = (f"INSERT INTO User "
           f"({columns}) "
           f"VALUES (%s, %s, %s, %s, %s)")
    mycursor.execute(add, list_to_add)
    mydb.commit()
    return f"L'utilisateur {name} {prenom} a été créé"


@app.put("/coach/update/{id_user}")
def update_user(id_user: int, prenom: Optional[str] = None, name: Optional[str] = None, mail: Optional[str] = None,
                date_naissance: Optional[datetime.datetime] = None, adresse: Optional[str] = None,
                last_coaching: Optional[datetime.datetime] = None):
    update = (prenom, name, mail, date_naissance, adresse, last_coaching)
    update_columns = ('prenom', 'name', 'mail', 'date_naissance', 'adresse', 'last_coaching')
    index = []
    for k in range(len(update)):
        if update[k]:
            index.append(k)
    print(index)
    # update = [update[k] for k in index]
    print(update)
    # update_columns = [update_columns[k] for k in index]
    print(update_columns)
    # update_columns = ', '.join(update_columns)
    for k in index:
        update_commande = ("UPDATE User "
                          f"SET {update_columns[k]} = '{update[k]}' "
                          f"WHERE id_user = {id_user}")
        print(update_commande)
        mycursor.execute(update_commande)
        mydb.commit()
    return f"L'utilisateur {id_user} a été modifié pour les paramètres {[update_columns[k] for k in index]}"


@app.delete("/coach/delete/{id_user}")
def delete_user(id_user: int):
    mycursor.execute(f"""DELETE FROM User
                        WHERE id_user = {id_user}""")
    mydb.commit()
    return f"L'utilisateur {id_user} a été supprimé"


@app.get("/coach/customers/infos")
def list_customers():
    mycursor.execute(f"""SELECT * FROM User""")
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/{id_user}/{date_message}")
def get_emotion_date(id_user: int, date_message: datetime.datetime):
    mycursor.execute(f"""SELECT Emotion.nom_emotion, Emotion.rate_emotion 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message = '{date_message}')"""
                        )
    emotions = mycursor.fetchall()
    arr_emotions = np.array(emotions)
    sentiment_maj = arr_emotions[np.argmax(arr_emotions[:,1])][0]
    mycursor.execute(f"""SELECT Daily_message.text 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message = '{date_message}')"""
                        )
    message = mycursor.fetchall()
    return {'Message': message, 'Sentiment majoritaire': sentiment_maj, 'Emotions': arr_emotions}


@app.get("/coach/customers/sentiments/{id_user}")
def get_emotion_range(id_user: int, date_inf: datetime.datetime, date_supp: datetime.datetime):
    mycursor.execute(f"""SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (User.id_user = {id_user} AND Daily_message.date_message > '{date_inf}'
                     AND Daily_message.date_message < '{date_supp}') 
                     GROUP BY Emotion.nom_emotion"""
                        )
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/global/message/")
def get_emotion_global(date_inf: datetime.datetime, date_supp: datetime.datetime):
    mycursor.execute(f"""SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) 
                     FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                     LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                     WHERE (Daily_message.date_message > '{date_inf}'
                     AND Daily_message.date_message < '{date_supp}') 
                     GROUP BY Emotion.nom_emotion"""
                        )
    return mycursor.fetchall()


@app.get("/coach/customers/sentiments/global/personne/")
def get_emotion_global(date_inf: datetime.datetime, date_supp: datetime.datetime):
    mycursor.execute(f"""SELECT nom_emotion, AVG(rate) FROM (
    SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) as rate,
    User.id_user FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user
    LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message WHERE (Daily_message.date_message > '{date_inf} '
    AND Daily_message.date_message < '{date_supp}]')  GROUP BY User.id_user, Emotion.nom_emotion
    )
    AS t GROUP BY nom_emotion;"""
                        )
    return mycursor.fetchall()



# SELECT nom_emotion, AVG(avg) FROM (
#     SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) as avg,
# User.id_user FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user
# LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message WHERE (Daily_message.date_message > '2015-09-08 00:15:01 '
# AND Daily_message.date_message < '2020-09-08 00:15:01')  GROUP BY User.id_user, Emotion.nom_emotion
# )
# AS t GROUP BY nom_emotion;


mycursor.execute(f"""SELECT Emotion.nom_emotion, AVG(Emotion.rate_emotion) 
                 FROM User LEFT JOIN Daily_message on Daily_message.id_user = User.id_user 
                 LEFT JOIN Emotion on Emotion.id_message = Daily_message.id_message 
                 WHERE (User.id_user = 3 AND Daily_message.date_message > '2015-09-08 00:15:01'
                  AND Daily_message.date_message < '2020-09-08 00:15:01')
GROUP BY Emotion.nom_emotion"""
                 )
testons = mycursor.fetchall()
print(testons)
# nptestons = np.array(testons)
# for emo in np.unique(nptestons[:,0]):
#     list_emo = [float(pair[1]) for pair in nptestons if pair[0] == emo]
#     print(list_emo)
#     print(emo, sum(list_emo), len(list_emo))
#     somme = 0
#     count = 0
#     for pair in nptestons:
#         if pair[0] == emo:
#             somme = somme + float(pair[1])
#             count = count + 1
#     print(emo, somme, count, somme/count)
# print(testons)
# print(np.unique(nptestons[:,0]))
# print(nptestons[:, 1])
# print(np.argmin(nptestons[:,1]))
# print(nptestons[np.argmax(nptestons[:,1])][0])
# print(type(testons))
# testons = testons.replace("T", " ")
# print(len(testons))

# testons = mycursor.fetchall()[0][0].isoformat()
# testons = testons.replace("T", " ")
# print(type(testons))


