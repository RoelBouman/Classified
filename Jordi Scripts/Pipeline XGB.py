# -*- coding: utf-8 -*-
"""
Created on Tue Apr 04 14:12:42 2017

@author: Gebruiker
"""
#%%
#Load libraries
import cPickle as pickle
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LogisticRegression
#from sklearn.ensemble import DecisionTreeClassifier as RF
#from sklearn.neighbors import KNeighborsClassifier as RF
from sklearn.metrics import accuracy_score as ACC
from sklearn.metrics import log_loss
from sklearn.metrics import confusion_matrix as  CM
#from sklearn import preprocessing 
from sklearn.model_selection import StratifiedKFold as SKF
#from sklearn.feature_extraction.text import TfidfVectorizer
import scipy as sp
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

#%% Load general information and data
gendir = './general/'
train_labels = pickle.load(open(gendir + 'labels.p',"rb"))
nclasses = pickle.load(open(gendir + 'nclasses.p',"rb"))
label_encoding = pickle.load(open(gendir + 'label_encoding.p',"rb"))
device_names = pickle.load(open(gendir + 'device_names.p',"rb"))
Monday_DevAc = pickle.load(open(gendir + 'Monday_Device_Activity.p',"rb"))
Tuesday_DevAc = pickle.load(open(gendir + 'Tuesday_Device_Activity.p',"rb"))
Wednesday_DevAc = pickle.load(open(gendir + 'Wednesday_Device_Activity.p',"rb"))
Thursday_DevAc = pickle.load(open(gendir + 'Thursday_Device_Activity.p',"rb"))
Friday_DevAc = pickle.load(open(gendir + 'Friday_Device_Activity.p',"rb"))
Saturday_DevAc = pickle.load(open(gendir + 'Saturday_Device_Activity.p',"rb"))
Sunday_DevAc = pickle.load(open(gendir + 'Sunday_Device_Activity.p',"rb"))
W17_DevAc = pickle.load(open(gendir + 'Week_17_Activity.p',"rb"))
W18_DevAc = pickle.load(open(gendir + 'Week_18_Activity.p',"rb"))
W1718_DevAc = pickle.load(open(gendir + 'Week_1718_Activity.p',"rb"))
Week_DevAc = pickle.load(open(gendir + 'Week_Device_Activity.p',"rb"))
NW_DevAc = pickle.load(open(gendir + 'Normalized_Week_Active.p',"rb"))
NH_DevAc = pickle.load(open(gendir + 'Normalized_Hour_Active.p',"rb"))
ND_DevAc = pickle.load(open(gendir + 'Normalized_Day_Active.p',"rb"))
#%%Load Features 

train_features = []
feature_names = []

for filename in os.listdir('./Train_features/'):
        train_features.append(pickle.load(open('./Train_features/' + filename,"rb")))
        feature_names.append(filename)
    
test_features = []

for filename in os.listdir('./Test_features/'):
        test_features.append(pickle.load(open('./Test_features/' + filename,"rb")))
    
#%% Combine Features

X_train_full = sp.sparse.hstack(train_features, format = 'csr')
X_test_full = sp.sparse.hstack(test_features, format = 'csr')

#%%
#Create cross-validation splits (10-fold)
n = 5
skf1 = SKF(n_splits = n)

#%%
#Cross validating loop
test_acc = np.zeros(n)
loss = np.zeros(n)

confmat = np.zeros((len(np.unique(train_labels)),len(np.unique(train_labels))))
i=0

#Single loop: testing is done by submitting near-optimal results to Kaggle.
for train_index, test_index in skf1.split(np.zeros(len(train_labels)),train_labels):
     print 'start iteration ' + str(i)
     
     X_train = X_train_full[train_index]
     X_test = X_train_full[test_index]
     
     Y_train = train_labels[train_index]
     Y_test = train_labels[test_index]
     d_train = xgb.DMatrix(X_train, label=Y_train)
     d_valid = xgb.DMatrix(X_test, label=Y_test)
     
     watchlist = [(d_train, 'train'), (d_valid, 'eval')]
     #-----------------------------------------------------------
     #Train classifier
     #-----------------------------------------------------------     
     
     #clf = RF(n_estimators=100, class_weight='balanced')
     print 'XGBoost Performance'

     params = {}
     params['booster'] = 'gblinear'
     params['objective'] = "multi:softprob"
     params['eval_metric'] = 'mlogloss'
     params['eta'] = 0.0005
     params['num_class'] = 12
     params['lambda'] = 3
     params['alpha'] = 1

     clf = xgb.train(params, d_train, 1000, watchlist, early_stopping_rounds=25)

     pred = clf.predict(xgb.DMatrix(X_test))
     #-----------------------------------------------------------
     #Evaluate classifier
     #-----------------------------------------------------------
     test_pred = clf.predict(xgb.DMatrix(X_test))
     i=i+1
     print 'end iteration ' + str(i)
#%% Final prediction and csv saving
print 'starting final prediction'
#clf = RF(n_estimators=100, class_weight='balanced')
params = {}
params['booster'] = 'gblinear'
params['objective'] = "multi:softprob"
params['eval_metric'] = 'mlogloss'
params['eta'] = 0.001
params['num_class'] = 12
params['lambda'] = 3
params['alpha'] = 1

clf = xgb.train(params, d_train, 1000, watchlist, early_stopping_rounds=10)

pred = clf.predict(xgb.DMatrix(X_test_full))
#clf.fit(X_train_full,train_labels)
pred = pd.DataFrame(pred, index = device_names, columns=label_encoding)

pred.to_csv('sparse_xgb.csv',index=True)