import sys
import pandas as pd
import numpy as np

import sklearn
from sklearn import set_config
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

import tensorflow as tf
import keras

from keras import layers
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Input
from keras.optimizers import Adam


if len(sys.argv) < 4:
    print('Error: Expected train, test, and submit filenames')
    print(f'Usage: {sys.argv[0]} <train.csv> <test.csv> <submit.csv>')
    exit(1)
    
set_config(transform_output="pandas")
RANDOM_STATE=42
np.random.seed(RANDOM_STATE)
tf.random.set_seed(RANDOM_STATE)

train_file  = sys.argv[1]
test_file   = sys.argv[2]
submit_file = sys.argv[3]

df_train = pd.read_csv(train_file)
df_test = pd.read_csv(test_file)

objective_cols = ['diagnosis', 'cancer_subtype']
df_train.drop(columns=['cancer_stage'], inplace=True)

x_train = df_train.drop(columns=objective_cols)
x_test = df_test

from sklearn.impute import SimpleImputer
imp = SimpleImputer(strategy='median')
x_train = imp.fit_transform(x_train)
x_test  = imp.transform(x_test)

scaler = StandardScaler()
x_train = scaler.fit_transform(x_train)
x_test  = scaler.fit_transform(x_test)

y0 = (df_train['diagnosis'] != 'No Cancer').astype(int)

label_diag = LabelEncoder()
y1 = label_diag.fit_transform(df_train['diagnosis'])

label_subtype = LabelEncoder()
y2 = label_subtype.fit_transform(df_train['cancer_subtype'])

num_classes_diag = len(label_diag.classes_)
num_classes_subtype = len(label_subtype.classes_)

def build_bin_model(dim):
    model = Sequential([
        Input(shape=(dim,)),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    model.compile(
        optimizer=Adam(learning_rate=1e-4, clipnorm=1.0),
        loss='binary_crossentropy',
        metrics=['accuracy']
        )
    return model

def build_multi_class_model(dim, num_classes):
    model = Sequential([
        Input(shape=(dim,)),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(
        optimizer=Adam(learning_rate=1e-4, clipnorm=1.0),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

y1_cat = to_categorical(y1, num_classes=num_classes_diag)
y2_cat = to_categorical(y2, num_classes=num_classes_subtype)

params=dict(
    epochs=50,
    batch_size=32,
    validation_split=0.1,
)

bin_model = build_bin_model(x_train.shape[1])
bin_model.fit(x_train, y0, **params)

diag_model = build_multi_class_model(x_train.shape[1], num_classes_diag)
diag_model.fit(x_train, y1_cat, **params)

subtype_model = build_multi_class_model(x_train.shape[1], num_classes_subtype)
subtype_model.fit(x_train, y2_cat, **params)

submission = pd.DataFrame()
submission['id'] = df_test['id']

submission['has_cancer'] = bin_model.predict(x_test).flatten()
submission['has_cancer'] = submission['has_cancer'].apply(lambda x: 'Yes' if x > 0.5 else 'No')

pred_diag = np.argmax(diag_model.predict(x_test), axis=1)
pred_subtype = np.argmax(subtype_model.predict(x_test), axis=1)

submission['type'] = label_diag.inverse_transform(pred_diag)
submission['subtype'] = label_subtype.inverse_transform(pred_subtype)

submission.to_csv(submit_file, index=False)
