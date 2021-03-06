# -*- coding: utf-8 -*-
"""hw2_svm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rQ8aXRV79VOE2sD9QAweBXjxYFWF8zdO
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cvxopt
from cvxopt import matrix as cvx_opt_matrix
from cvxopt import solvers as cvx_opt_solvers

data=pd.read_csv("hw2data.csv",header=None);
index = [i for i in range(data.shape[0])]
np.random.shuffle(index)
data=data.set_index([index]).sort_index()
bound=int(0.8*data.shape[0]);
train=data[:bound]
test=data[bound:]

Y=train[2]
X=train[train.columns.difference([2])]
#X=(X-X.mean())/X.std()
no_of_folds=10
X_test=test[test.columns.difference([2])]
#X_test=(X_test-X_test.mean())/X_test.std()
Y_test=pd.DataFrame();
Y_test=pd.concat([Y_test, test[2]])

def splitData(itr):
  X_shuffled={};
  Y_shuffled={};
  size=int(len(X)/itr);
  start=0;
  for iterating_var in range(0,itr):
    X_shuffled[iterating_var+1]=X[start:size*(iterating_var+1)];
    Y_shuffled[iterating_var+1]=Y[start:size*(iterating_var+1)];
    start=size*(iterating_var+1);
  return X_shuffled,Y_shuffled;

def getnexttrainvalid(X_shuffled, Y_shuffled, itr):
  X_train=pd.DataFrame();
  Y_train=pd.DataFrame(); 
  X_valid=pd.DataFrame();
  Y_valid=pd.DataFrame();
  for iterating_var in range(0,no_of_folds):
    if iterating_var!=itr:
      X_train=X_train.append(X_shuffled.get(iterating_var+1));
      Y_train=pd.concat([Y_train, Y_shuffled.get(iterating_var+1)]);
    else:
      X_valid=X_shuffled.get(iterating_var+1);
      Y_valid=pd.concat([Y_valid, Y_shuffled.get(iterating_var+1)])
  return X_train,Y_train,X_valid,Y_valid;

def RBF_Kernel_Matrix(X,Y):
  gamma=0.5
  return np.exp(-gamma*np.linalg.norm(X-Y)**2)

def optimizer(y,K,n_r,C):
  P = cvxopt.matrix(np.outer(y, y) * K)
  q = cvxopt.matrix(np.ones(n_r) * -1)
  A = cvxopt.matrix(y, (1, n_r))
  b = cvxopt.matrix(np.zeros(1))
  
  G= cvx_opt_matrix(np.vstack((np.eye(n_r)*-1,np.eye(n_r))));
  h = cvx_opt_matrix(np.hstack((np.zeros(n_r), np.ones(n_r) * C)));
  return cvxopt.solvers.qp(P, q, G, h, A, b);

def rbf_svm_train(X_train,y,C):
  n_r, n_f = X_train.shape;
  K = np.zeros((n_r, n_r))
  for i in range(n_r):
    for j in range(n_r):
      K[i, j] = RBF_Kernel_Matrix(X_train[i], X_train[j])

  Solution = optimizer(y,K,n_r,C)

  alpha =  np.ravel(Solution['x'])

  idx = alpha > 1e-10
  lagr_value = alpha[idx]
  support_vectors = X_train[idx]
  support_vector_labels = y[idx]
  intercept = support_vector_labels[0]
  for i in range(len(lagr_value)):
    intercept -= lagr_value[i] * support_vector_labels[i] * RBF_Kernel_Matrix(support_vectors[i], support_vectors[0])

  return support_vectors, support_vector_labels, lagr_value, intercept

def svm_fit(X_train,y,C):
  n_r, n_f = X_train.shape;
  K = np.zeros((n_r, n_r))
  #for i in range(n_r):
   # for j in range(n_r):
   #   K[i, j] = np.dot(X_train[i], X_train[j].T)
  K=np.dot(X_train, X_train.T)

  Solution = optimizer(y,K,n_r,C)

  alpha = np.ravel(Solution['x'])

  idx = alpha > 1e-10
  lagr_value = alpha[idx]
  support_vectors = X_train[idx]
  support_vector_labels = y[idx]

  intercept = support_vector_labels[0]
  for i in range(len(lagr_value)):
    intercept -= lagr_value[i] * support_vector_labels[i] * np.dot(support_vectors[i], support_vectors[0].T)

  return support_vectors, support_vector_labels, lagr_value, intercept

def rbf_svm_predict(X_train, support_vectors, support_vector_labels, lagr_value, intercept):
  y_pred = []
  for x_train in X_train:
    prediction = 0
    for i in range(len(lagr_value)):
      prediction += lagr_value[i] * support_vector_labels[i] * RBF_Kernel_Matrix(support_vectors[i], x_train)
    prediction += intercept
    y_pred.append(np.sign(prediction))
  return np.array(y_pred)

def predict(X_train, support_vectors, support_vector_labels, lagr_value, intercept):
  y_pred = []
  for x_train in X_train:
    prediction = 0
    for i in range(len(lagr_value)):
      prediction += lagr_value[i] * support_vector_labels[i] * np.dot(support_vectors[i], x_train.T)
    prediction += intercept
    y_pred.append(np.sign(prediction))
  return np.array(y_pred)

def error(target,predicted):
  target=abs(target-predicted);
  res=0;
  for i in range(0,target.shape[0]):
    if target[i]>0:
      res+=1;
  return res/target.shape[0];

def model(C):
  X_shuffled,Y_shuffled=splitData(no_of_folds);
  err_train=0;
  err_test=0;
  err_CV=0;
  for itr in range(0,no_of_folds):
    X_train,Y_train,X_valid,Y_valid=getnexttrainvalid(X_shuffled,Y_shuffled,itr);
    support_vectors, support_vector_labels, lagr_value, intercept=svm_fit(X_train.values, Y_train.values,C);
    res=predict(X_valid.values,support_vectors,support_vector_labels, lagr_value, intercept);
    res_train=predict(X_train.values, support_vectors, support_vector_labels, lagr_value, intercept);
    res_test=predict(X_test.values, support_vectors, support_vector_labels, lagr_value, intercept);
    err_train+=error(res_train,Y_train.values);
    err_CV+=error(res,Y_valid.values);
    err_test+=error(res_test,Y_test.values);
  err_train/=10;
  err_CV/=10;
  err_test/=10;
  return err_train,err_CV,err_test;

error_train=[];
error_test=[];
error_cv=[];
C=[0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000];
#C=[100];
for c in C:
  err_train,err_CV,err_test=model(c);
  error_train.append(err_train);
  error_cv.append(err_CV);
  error_test.append(err_test);

plt.plot(C,error_test,label="Test")
plt.plot(C,error_train,label="Train")
plt.plot(C,error_cv,label="CV")
plt.title("Error-C graph Linear SVM ")
plt.xlabel("C")
plt.ylabel("Error")
plt.legend()

print(error_test)

print(error_train)

print(error_cv)

