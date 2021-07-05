"""Create the tables on sql using mysql"""

import mysql.connector

# Connection to MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="student"
)


# Cursor initialization
mycursor = mydb.cursor()

# Database creation
mycursor.execute("CREATE DATABASE IF NOT EXISTS onlinediary;")
mycursor.execute("USE onlinediary;")


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
