from fastapi import FastAPI, Form
import mysql.connector
from typing import Optional
import datetime
from fonctions import update_emotions, add_in_database
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
async def read_messages(id_user: int, date: Optional[str] = None):
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


# @app.put("/user/{id_user}/create")
# async def create_message(id_user: int, message: str):
#     date_message = datetime.datetime.today()
#     date_message = date_message.strftime("%Y/%m/%d %H:%M:%S")
#     columns_mess = 'id_user, text, date_message'
#     columns_emotion = 'id_message, nom_emotion, rate_emotion'
#     classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
#     model = keras.models.load_model('../modelNLP')
#     add_in_database((id_user, message, date_message), 'Daily_message', columns_mess)
#     predictions = model.predict([message])[0]
#     mycursor.execute(f"""SELECT id_message
#                                 FROM Daily_message
#                                 WHERE id_user = {id_user}
#                                 ORDER BY date_message DESC;
#                             """)
#     id_message = mycursor.fetchall()[0][0]
#     for j in range(len(classes)):
#         rate = predictions[j]
#         emotion = classes[j]
#         add_in_database((id_message, emotion, rate), 'Emotion', columns_emotion)


mycursor.execute("""SELECT id_message FROM Daily_message
WHERE date_message > '2021-04-30 17:53:19'
AND id_user = 1
""")
testons = mycursor.fetchall()[0][0]
print(testons)
# testons = testons.replace("T", " ")
# print(len(testons))

# testons = mycursor.fetchall()[0][0].isoformat()
# testons = testons.replace("T", " ")
print(type(testons))


