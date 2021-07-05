"""Contains the functions used in the other files"""

import mysql.connector
from tensorflow import keras
import joblib
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from emoji import demojize
import re
import sklearn
# import sys
# import os
# print('cwd fct: ', os.getcwd())
# print('path fct: ', sys.path)
# print('file fct: ', __file__)

# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)

# Cursor initialization
mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE onlinediary;")


def update_emotions(id_message, message):
    """"Given an id message and a message, compute emotions rates and update the emotion table."""
    classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
    # Preprocesses and makes the prediction for the message
    enc = load_enc()
    prep_message = preprocessing(message, enc)
    model = load_model()
    predictions = model.predict_proba(prep_message)[0]
    # Update the emotion table for each emotion
    for j in range(len(classes)):
        rate = predictions[j]
        emotion = classes[j]
        update = ("UPDATE Emotion "
                  f"SET rate_emotion = {rate} "
                  f"WHERE nom_emotion = '{emotion}' "
                  f"AND id_message = {id_message}")
        mycursor.execute(update)
        mydb.commit()


def create_emotion(id_message, message):
    """"Given an id message and a message, compute emotions rates and create rows in the emotion table."""
    columns_emotion = 'id_message, nom_emotion, rate_emotion'
    classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
    # Preprocesses and makes the prediction for the message
    enc = load_enc()
    prep_message = preprocessing(message, enc)
    model = load_model()
    predictions = model.predict_proba(prep_message)[0]
    # Create the rows in emotion table for each emotion
    for j in range(len(classes)):
        rate = predictions[j]
        emotion = classes[j]
        add_in_database((id_message, emotion, rate), 'Emotion', columns_emotion)


def add_in_database(list_to_add, table, columns):
    """Add a list of elements in the database given a list of elements to add, a table and the table columns to add."""
    add = (f"INSERT INTO {table} "
           f"({columns}) "
           f"VALUES {list_to_add}")
    # Try to execute the query to add the given list to the columns' table
    try:
        mycursor.execute(add)
    # If it doesn't work, print that the list is already existing in the table
    except:
        print(f"{list_to_add} est déjà présent dans la base {table}")
    mydb.commit()


def lemmatizer(text):
    """Apply Wordnet lemmatizer to text (go to root word)"""
    wnl = WordNetLemmatizer()
    text = [wnl.lemmatize(word) for word in text.split()]
    return " ".join(text)


# suppression des caratères spéciaux, formatage des contractions...


def clean_str(texts):
    """Given a texts, remove special characters, replace contracted form and stopwords"""

    # Lowercasing
    texts = texts.str.lower()

    # Remove special chars
    texts = texts.str.replace(r"(http|@)\S+", "")
    texts = texts.apply(demojize)
    texts = texts.str.replace(r"::", ": :")
    texts = texts.str.replace(r"’", "'")
    texts = texts.str.replace(r"[^a-z\':_]", " ")

    # Remove repetitions
    pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
    texts = texts.str.replace(pattern, r"\1")

    # Transform short negation form
    texts = texts.str.replace(r"(can't|cannot)", 'can not')
    texts = texts.str.replace(r"(ain't|wasn't|weren't)", 'be not')
    texts = texts.str.replace(r"(don't|didn't|didnt)", 'do not')
    texts = texts.str.replace(r"(haven't|hasn't)", 'have not')
    texts = texts.str.replace(r"(won't)", 'will not')
    texts = texts.str.replace(r"(im)", ' i am')
    texts = texts.str.replace(r"(ive)", ' i have')
    texts = texts.str.replace(r"(n't)", ' not')

    # Remove stop words
    stopword = stopwords.words('english')
    stopword.remove('not')
    stopword.remove('nor')
    stopword.remove('no')
    texts = texts.apply(lambda x: ' '.join([word for word in x.split() if (word not in stopword and len(word) > 1)]))
    return texts


def preprocessing(text, enc):
    """Apply all the preprocessing (cleaning and encoding) for a given text"""
    return enc.transform(clean_str(pd.Series(lemmatizer(text))).values)


def load_model():
    """Import the model to predict the emotions"""
    return joblib.load("../dump/model_forest.joblib")


def load_enc():
    """Return the encoder to prepare the text"""
    return joblib.load("../dump/tfidf_encoder.joblib")
