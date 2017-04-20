import pandas as pd 
import numpy as np
from matplotlib import pyplot

from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error

import sys
import time

import xgboost as xgb

folds = 7
seed = 7

model='xgb'

def rmse_cv(model, X_train, y_train):
    kfold = KFold(n_splits=folds, random_state=seed)
    rmse = np.sqrt(-cross_val_score(model, X_train, y_train, scoring="neg_mean_squared_error", cv = kfold))
    return(rmse)

def main(predictions = False):

    # ----------------------------------------------------------------------------

    data = pd.read_csv("./data/clean_dataset.csv")

    train = data.loc[data.set == 'train', data.columns.values[1:]]
    test = data.loc[data.set == 'test', data.columns.values[1:]]

    X_train = train.drop(['Id', 'SalePrice', 'logSalePrice', 'set'], axis=1)
    y_train = np.log1p(train['SalePrice'])

    X_test = test.drop(['Id', 'SalePrice', 'logSalePrice', 'set'], axis=1)

    # ----------------------------------------------------------------------------

    # build model
    model_xgb = xgb.XGBRegressor(
        n_estimators=250,
        learning_rate=0.2,
        max_depth=2,
        min_child_weight=0.8,
        objective='reg:linear'
    )

    # fit model
    model_xgb.fit(X_train, y_train, verbose=True)

    # evaluate model
    results = rmse_cv(model_xgb, X_train, y_train)
    print("RMSE-{}-CV({})={:06.5f}+-{:06.5f}".format(model, folds, results.mean(), results.std()))

    # # predict
    if predictions:
        y_test_pred_log = model_xgb.predict(X_test)
        y_test_pred = np.expm1(y_test_pred_log)
        submission = pd.DataFrame({'Id':test['Id'], 'SalePrice':y_test_pred})

        subFileName = "./submissions/sub-" + model + "-" + time.strftime("%Y%m%d-%H%M%S") + ".csv"
        print("saving to file: " + subFileName)
        submission.to_csv(subFileName, index=False)
        

# ----------------------------------------------------------------------------


if __name__ == "__main__":
    savePredict = False
    if len(sys.argv) > 1:
        if sys.argv[1] == 'save':
            savePredict = True
    main(predictions = savePredict)