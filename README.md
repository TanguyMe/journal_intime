# online_diary

## Context:

Create a database where the user can write a message every day for a coaching app. A model runs to predict what are the feeling of the users considering his message. The coach can access users personnal informations, modify them and visualize the feeling of his customers.

## Files: 

**/data:** contains the text data to fill the database  
**/dump:** contains the random forest model and the encoder (tfidf_vectorizer) used with it  
**/modelNLP:** contains the NLP model (currently not working with the api, hence the random forest model that is less efficient but is working)  
**requirements.txt:** contains the required versions of the used libraries  
**src/CreateDB.py:** Script to create the database, run it first  
**src/FillDB.py:** Script to fill the database, run it after CreateDB if you want to fill the database with random text and users. Enter the parameters (users to add and messages to add) at the beginning of the script and run  
**src/api.py:** Script to run the API for both the coach and the users  
**src/app.py** Script to run the streamlit app for the coach and the users. Api needs to run for this script to work  
**src/fonctions.py** Script that contains the functions used in the other scripts  
**src/test:** Folder that contains the tests. Pytest has to run from there to work properly  
**src/test/test_modele.py** Script to test the model and the functions  
**src/test/test_api.py** Script to test the api, not complete (and not fully working) at the moment  
