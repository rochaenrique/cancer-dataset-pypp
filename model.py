import sys
import pandas as pd
import numpy as np
from sklearn import set_config
from sklearn.svm import SVC
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.preprocessing import RobustScaler, StandardScaler, MinMaxScaler, QuantileTransformer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.feature_selection import SelectKBest, f_classif


def score(pipe, X, y0, y1, y2):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    score0 = cross_val_score(pipe, X, y0, cv=cv).mean()
    score1 = cross_val_score(pipe, X, y1, cv=cv).mean()
    score2 = cross_val_score(pipe, X, y2, cv=cv).mean()
    print(f'has_cancer score: {score0}')
    print(f'diagnosis  score: {score1}')
    print(f'subtype    score: {score2}')
    print(f'kaggle pred: {0.5 * score0 + 0.3 * score1 + 0.2 * score2}')

if len(sys.argv) < 4:
    print('Error: Expected train, test, and submit filenames')
    print(f'Usage: {sys.argv[0]} <train.csv> <test.csv> <submit.csv>')
    exit(1)

train_file  = sys.argv[1]
test_file   = sys.argv[2]
submit_file = sys.argv[3]

RANDOM_STATE=21

# print(f'Training data file: {train_file}')
# print(f'Test data file    : {test_file}')
# print(f'Output data file  : {submit_file}')

set_config(transform_output="pandas")

df_train = pd.read_csv(train_file)
df_test = pd.read_csv(test_file)

objective_cols = ['diagnosis', 'cancer_subtype', 'cancer_stage']
y = df_train[objective_cols]
y1 = y['diagnosis']
y2 = y['cancer_subtype']
y0 = y.diagnosis != 'No Cancer'

svm_pipeline = Pipeline([
    ('scaler', RobustScaler()),
    ('svm', SVC(kernel='rbf', probability=True, class_weight='balanced'))
])

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('classification', LogisticRegression(solver='newton-cholesky', n_jobs=-1, random_state=RANDOM_STATE))
    # ('classification', SGDClassifier(
    #     tol                 = 0.4,
    #     eta0                = 0.2,
    #     alpha               = 0.2,
    #     epsilon             = 0.01,
    #     power_t             = 0.9,
    #     validation_fraction = 0.1,
    #     loss                = 'hinge',
    #     learning_rate       = 'constant',
    #     random_state        = RANDOM_STATE,
    #     fit_intercept       = False,
    #     shuffle             = True,
    #     average             = 1,
    #     n_jobs              = -1,
    # )),
    # ('classification', RandomForestClassifier(
    #     n_estimators = 100,
    #     criterion    = 'log_loss',
    #     max_depth    = 2,
    #     min_samples_split = 10,
    #     min_samples_leaf = 2,
    #     min_weight_fraction_leaf = 0.01,
    #     max_leaf_nodes = 5,
    #     ccp_alpha = 1.0,
    #     random_state = RANDOM_STATE,
    #     n_jobs       = -1,
    # )),
])

X = df_train.drop(columns=objective_cols)

has_cancer_classifier = clone(pipe).fit(X, y0)
diagnosis_classifier  = clone(pipe).fit(X, y1)
subtype_classifier    = clone(pipe).fit(X, y2)

score(pipe, X, y0, y1, y2)

submission = pd.DataFrame()
submission['id'] = df_test.id
submission['has_cancer'] = pd.Series(has_cancer_classifier.predict(df_test)).apply(lambda x: 'Yes' if x else 'No')
submission['type']    = diagnosis_classifier.predict(df_test)
submission['subtype'] = subtype_classifier.predict(df_test)

submission.to_csv(submit_file, index=False)
