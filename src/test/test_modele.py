"""Test the model and the functions"""

import joblib
import sys
import os
# print('paths test:', sys.path)
# print('cwd test: ', os.getcwd())
# Ajout du path pour pytest
sys.path.append(os.path.join(sys.path[0], 'journal_intime'))
# sys.path.append(os.path.join(sys.path[-1],'src', 'test'))
# Ajout du path pour
# print(sys.path[0])
# print(os.getcwd())
from src.fonctions import preprocessing
from src.app import get_data, check_integer

# sys.path.append("../..")
# import os
#
# print(__file__ + "get cwd " + os.getcwd())

print(__file__)


class TestModele:
    """Class to test the model"""
    model = joblib.load("../../dump/model_forest.joblib")
    enc = joblib.load("../../dump/tfidf_encoder.joblib")
    classes = ['anger', 'fear', 'happy', 'love', 'sadness', 'surprise']

    def test_dim(self):
        """Test that 6 emotions are predicted"""
        assert len(self.model.predict_proba(preprocessing("Sample phrase", self.enc))[0] == 6)

    def test_predict(self):
        """Test that the right emotion is returned for a given sentence"""
        index_predict = int(self.model.predict(preprocessing("I am so happy, it's very fun and enjoyable", self.enc)))
        assert self.classes[index_predict] == 'happy'


def test_get_data():
    """Test that the data from User table is the right size"""
    data = get_data()
    assert data.shape[1] == 7


def test_check_integer():
    """Test that it returns True for int and False for text"""
    assert check_integer(15)
    assert not check_integer('Text')
