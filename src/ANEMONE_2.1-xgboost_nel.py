# First XGBoost model for Pima Indians dataset
import os
import numpy as np
import json

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from util.config import ANEMONE_DATASET_STORE_PATH, ANEMONE_XGBOOST_DATASET_FILE_NAME, JAVADOC_GLOBAL_NAME
# load data
with open(os.path.join(ANEMONE_DATASET_STORE_PATH[JAVADOC_GLOBAL_NAME], ANEMONE_XGBOOST_DATASET_FILE_NAME), 'r', encoding='utf-8') as rf:
    dataset = np.array(json.load(rf))
    # split data into X and y
X = dataset[:, 0:2]
Y = dataset[:, 2]
# split data into train and test sets
seed = 7
test_size = 0.2
X_train, X_test, y_train, y_test = train_test_split(
    X, Y, test_size=test_size, random_state=seed)
# fit model no training data
model = XGBClassifier()
model.fit(X_train, y_train)
# make predictions for test data
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))
