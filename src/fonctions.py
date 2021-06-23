import mysql.connector
from tensorflow import keras
import joblib
import pandas as pd
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from emoji import demojize
import re
import sklearn

# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)

# Cursor initialization
mycursor = mydb.cursor(buffered=True)
mycursor.execute("USE onlinediary;")


def update_emotions(id_message, message):
    columns_emotion = 'id_message, nom_emotion, rate_emotion'
    classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']
    print(classes)
    print('update' + message)
    print(type(message))
    prep_message = preprocessing(message)
    predictions = model.predict_proba(prep_message)[0]
    for j in range(len(classes)):
        rate = predictions[j]
        emotion = classes[j]
        update = ("UPDATE Emotion "
                  f"SET rate_emotion = {rate} "
                  f"WHERE nom_emotion = '{emotion}' "
                  f"AND id_message = {id_message}")
        mycursor.execute(update)
        mydb.commit()
    # mydb.close()


def create_message()


def add_in_database(list_to_add, table, columns):
    add = (f"INSERT INTO {table}" 
               f"({columns})"
               f"VALUES {list_to_add}")
    try :
        mycursor.execute(add)
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
    # from nltk.corpus import stopwords

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
    texts = texts.apply(lambda x: ' '.join([word for word in x.split() if (word not in stopword and len(word) > 1 )]))
    return texts


def preprocessing(text):
    return enc.transform(clean_str(pd.Series(lemmatizer(text))).values)


model = joblib.load("../dump/model_forest.joblib")
enc = joblib.load("../dump/tfidf_encoder.joblib")

