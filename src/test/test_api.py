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
# Use test database
mycursor.execute("USE testdbdiary;")
# Adding a user to the test database
columns = 'nom, prenom, date_naissance, mail'
values_to_add = ('Schmidt', 'Walter', '1999-09-19', 'WalSchmi@mail.com')
mycursor.execute("INSERT INTO User"
                 f"({columns})"
                 f"VALUES {values_to_add}"
                 )
mydb.commit()


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


def test_read_message_content():
    """Test displaying the messages"""
    response = client.get("/user/1/read")
    assert response.status_code == 200
    assert response.json()[0][:3] == [1, 1, 'hello world']


def test_update_message():
    """Test updating message"""
    response = client.put("/user/1/update?message=Goodbye world")
    assert response.status_code == 200
    assert response.json() == {'id_user': 1, 'message': 'Goodbye world'}


def test_delete_user():
    """Test deleting the user"""
    response = client.delete("/coach/delete/1")
    assert response.status_code == 200
    assert response.json() == "L'utilisateur 1 a été supprimé"


# Drop test database after we used it
mycursor.execute('DROP DATABASE IF EXISTS testdbdiary;')
mydb.commit()
