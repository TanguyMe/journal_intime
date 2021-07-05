"""Test the API, create a test database"""

from fastapi.testclient import TestClient
import mysql.connector
import sys
import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from ..database import Base
# from ..main import app, get_db
#
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# Base.metadata.create_all(bind=engine)
# print('paths test:', sys.path)
# print('cwd test: ', os.getcwd())
# Ajout du path pour pytest
sys.path.append(os.path.join(sys.path[0], 'journal_intime'))
sys.path.append(os.path.join(sys.path[-1], 'src'))
# print('paths test:', sys.path)
# Ajout du path pour
# print(sys.path[0])
# print(os.getcwd())
from src.api import app


client = TestClient(app)


# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)


# Cursor initialization
mycursor = mydb.cursor(buffered=True)
# Drop database to have an empty one
mycursor.execute('DROP DATABASE IF EXISTS testdbdiary;')
# Test database creation
mycursor.execute("CREATE DATABASE IF NOT EXISTS testdbdiary;")
mycursor.execute("USE testdbdiary;")


# Create table User
mycursor.execute("""CREATE TABLE IF NOT EXISTS User (
                 id_user SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, 
                 nom VARCHAR(55), 
                 prenom VARCHAR(55), 
                 date_naissance DATE,
                 last_coaching DATE, 
                 adresse VARCHAR(55),
                 mail VARCHAR(55),
                 CONSTRAINT UC_User UNIQUE (prenom, nom, date_naissance, mail))
                 ENGINE = INNODB;""")

# Create table Daily_message
mycursor.execute("CREATE TABLE IF NOT EXISTS Daily_message("
                 "id_message MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, "
                 "id_user SMALLINT UNSIGNED NOT NULL, "
                 "text VARCHAR(280), "
                 "date_message DATETIME, "
                 "CONSTRAINT fk_user_daily_message FOREIGN KEY (id_user) "
                 "  REFERENCES User(id_user)"
                 "  ON DElETE CASCADE"
                 "  ON UPDATE CASCADE,"
                 "CONSTRAINT UC_Daily_message UNIQUE (id_user, date_message))"
                 "ENGINE = INNODB;")

# Create table Emotion
mycursor.execute("CREATE TABLE IF NOT EXISTS Emotion("
                 "id_message MEDIUMINT UNSIGNED NOT NULL, "
                 "nom_emotion VARCHAR(20), "
                 "rate_emotion FLOAT, "
                 "CONSTRAINT fk_daily_message_emotions FOREIGN KEY (id_message) "
                 "  REFERENCES Daily_message(id_message)"
                 "  ON DElETE CASCADE"
                 "  ON UPDATE CASCADE)"
                 "ENGINE = INNODB;")


def test_create_user():
    """Test creating user"""
    response = client.post('/coach/create?prenom=John&nom=Doe&mail=John.Doe@mail.com')
    assert response.status_code == 200
    assert response.json() == "L'utilisateur Doe John a été créé"


def test_update_user():
    """Test updating user"""
    response = client.put("/coach/update/1?prenom=Jean&nom=Dupont")
    assert response.status_code == 200
    assert response.json() == "L'utilisateur 1 a été modifié pour les paramètres ['prenom', 'nom']"


def test_create_message_valid():
    """Test creating a valid message"""
    response = client.post("/user/1/create?message=hello world")
    assert response.status_code == 200
    assert response.json() == {'id_user': 1, 'message': 'hello world'}


def test_create_message_invalid():
    """Test creating an invalid message"""
    response = client.post("/user/1/create?message=hello world")
    assert response.status_code == 200
    assert response.json() == 'Impossible d\'ajouter ce message. ' \
                              'Il y a déjà un message aujourd\'hui, veuillez le modifier.'


def test_delete_user():
    """Test deleting the user"""
    response = client.delete("/coach/delete/1")
    assert response.status_code == 200
    assert response.json() == "L'utilisateur 1 a été supprimé"
