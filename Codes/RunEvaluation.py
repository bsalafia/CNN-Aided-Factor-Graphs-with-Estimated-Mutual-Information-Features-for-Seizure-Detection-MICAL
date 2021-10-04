# -*- coding: utf-8 -*-
"""Copy of CNNSMILEGRU_Bs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Fgyv5Og_PPfexz3ih-4uEJqa-PfQsKSA
"""

import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="2"
from keras.models import Model
from keras.utils.generic_utils import get_custom_objects
from keras import optimizers, regularizers
import keras.backend as K
from keras import regularizers
from tensorflow.keras.layers import InputLayer
from keras.layers import Input
import time
import tensorflow as tf
import os
import scipy
import h5py
import glob, os
# import BaseLineModel
from scipy.io import loadmat
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
# from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten,Concatenate
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.metrics import f1_score,plot_roc_curve
from sklearn.metrics import plot_precision_recall_curve,roc_curve,roc_auc_score,auc
from sklearn.metrics import precision_recall_fscore_support,precision_recall_curve
import matplotlib.pyplot as plt;
from keras.optimizers import Adam
from keras.layers.normalization import BatchNormalization
from keras.utils import np_utils
from keras.layers import Conv1D, MaxPooling1D, ZeroPadding1D, GlobalAveragePooling1D
from keras.layers.advanced_activations import LeakyReLU
from keras.preprocessing.image import ImageDataGenerator
from sklearn import preprocessing
from keras import regularizers
from numpy import mean
from numpy import std
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.layers import InputLayer
from keras.layers import Input
# from google.colab import drive
from sklearn.model_selection import LeaveOneOut
import gc
gc.collect()

def PatientsName():

  Name=['chb01','chb02','chb03','chb04','chb05','chb06','chb07','chb08','chb09','chb10',
  'chb11','chb12','chb13','chb14','chb15','chb16','chb17','chb18','chb19','chb20','chb21',
  'chb22','chb23','chb24']
  return Name

def PatientsEDFFile(dirname):

  os.chdir(dirname)
  a=[]
  X=[]
  Y=[]
  k=0
  for file in glob.glob("*.mat"):
      a.append(file)
      # print(a)
  return a
##############################Read and organize the data############################################
def create_sub_seq(nn_input, len_ss, labels=None):

  """
  This function creates all sub sequences for the batch
  """
  n_seq = nn_input.shape[0]
  len_seq = nn_input.shape[1]
  n_ss = len_seq - len_ss + 1
  new_labels = []
  if nn_input.ndim == 3:
    new_inp = np.zeros((n_ss*n_seq,len_ss,nn_input.shape[2]))
  elif nn_input.ndim == 4:
    new_inp = np.zeros((n_ss*n_seq,len_ss,nn_input.shape[2], nn_input.shape[3]))
  if labels is not None:
      dim_labels = labels.shape
      if len(dim_labels) == 2:
          new_labels = np.zeros((n_ss*n_seq, len_ss))
      elif len(dim_labels) == 3:
          new_labels = np.zeros((n_ss * n_seq, len_ss, dim_labels[2]))
  k = 0
  for i in range(n_seq):
      for j in range(n_ss):
          new_inp[k] = nn_input[i, j:j + len_ss, :]
          if labels is not None:
              if len(dim_labels) == 2:
                  new_labels[k, :] = labels[i, j:j + len_ss]
              elif len(dim_labels) == 3:
                  new_labels[k, :, :] = labels[i, j:j + len_ss, :]
          k += 1
  return new_inp, n_ss, new_labels

def ReadMatFiles(dirname,indx, seq_len=1,diff=None):

  EDF=[]
  EDFFiles=[]
  Name=[]
  EDF=PatientsEDFFile(dirname)
  Name=PatientsName()
  Xfile=[]
  Yfile=[]
  ind=[]

  MI_all=[]
  X=[]
  Y=[]
  MI_diff_all=[]

  for j in list(indx):
    print(j)
    indices = [i for i, elem in enumerate(EDF) if Name[j] in elem]
    ind.append(indices)

  ind=np.concatenate(ind,axis=0)

  for k in range(len(ind)):
    # print(ind[k])
    matfile=loadmat(os.path.join(dirname,EDF[int(ind[k])]))
    x=matfile['X_4sec']
    y=matfile['Y_label_4sec']
    mi=matfile['estimated_MI']
    y=np.transpose(y)
    start_idx = np.argmax(y>0)
    a = y == 1
    end_idx = len(a) - np.argmax(np.flip(a)) - 1
    real_y = np.zeros_like(y)
    real_y[start_idx:end_idx+1] = 1
    MI=np.zeros((mi.shape[0],153))
    for j in range(mi.shape[0]):
      mi2=mi[j,:,:]
      mi_mod=list(mi2[np.triu_indices(18,k=1)])
      MI[j,:]=mi_mod


    MI_diff=[]
    if seq_len > 1:
      real_y = np.expand_dims(real_y, axis=0)
      x = np.expand_dims(x, axis=0)
      MI = np.expand_dims(MI, axis=0)
      # print(MI.shape)
      x, _ , real_y = create_sub_seq(x, seq_len, labels=real_y)
      MI, _, _ = create_sub_seq(MI, seq_len)


    if diff is not None:

      for j in range(MI.shape[0]-1):

        MI_diff.append(MI[j+1]-MI[j])

      MI_diff=np.array(MI_diff)
      MI=MI[1:]
      x=x[1:]
      real_y=real_y[1:]
    X.append(x)
    Y.append(real_y)
    MI_all.append(MI)
    MI_diff_all.append(MI_diff)

  #
  # X=np.concatenate(X,axis=0)
  # Y=np.concatenate(Y,axis=0)
  # MI_all=np.concatenate(MI_all,axis=0)
  # MI_diff_all=np.concatenate(MI_diff_all,axis=0)
  #
  # print(X.shape)
  # print(Y.shape)
  # print(MI_all.shape)
  # print(MI_diff_all.shape)

  return X, Y, MI_all, MI_diff_all
##############Specify the input for each model based on control parameters#############################
def Xtrain(cnn,smile,diff,twodcnn,x,y,mi,mi_diff):

  if cnn==1:
    X_train=x
  if smile==1:
    X_train=[x,mi]
  if diff==1:
    X_train=[x,mi,mi_diff]

  if twodcnn==1:
    x2d=x.reshape(x.shape[0],x.shape[2],x.shape[1],1)
    X_train=x2d

  return X_train





################Main function to calculate matrics######################################

def ModelTrain(dirname,modeldir,SaveResults,SaveResultsTruePred,modelname,seq_len,cnn,smile,diff,twodcnn,indx,gru,Noepoch):

  FoldNum=6
  kfold = KFold(n_splits=FoldNum, shuffle=False)
  start_time = time.time()
  fold_no=0

  savenamef1='fscore_'+modelname+'_'+indx+'_'+str(Noepoch)+'_'
  cfname='cfmat_'+modelname+'_'+indx+'_'+str(Noepoch)+'_'
  fprname='fpr_'+modelname+'_'+indx+'_'+str(Noepoch)
  tprname='tpr_'+modelname+'_'+indx+'_'+str(Noepoch)
  prname='PR_'+modelname+'_'+indx+'_'+str(Noepoch)
  rocname='ROC_'+modelname+'_'+indx+'_'+str(Noepoch)

  for th in [0.5]:
    fold_no=0

    fpr=[]
    tpr=[]
    PR=[]
    ROC=[]
    pred=[]
    act=[]
    fscore=[]

    for trainindx, testindx in kfold.split(range(24)):

      if indx=='test':
        ind=testindx
      else:
        ind=trainindx

      x, y, mi,mi_diff=ReadMatFiles(dirname,ind,seq_len,diff)

      X=np.concatenate(x,axis=0)
      Y=np.concatenate(y,axis=0)
      MI_all=np.concatenate(mi,axis=0)
      MI_diff_all=np.concatenate(mi_diff,axis=0)
      fold_no=fold_no+1


      X_train=Xtrain(cnn,smile,diff,twodcnn,X,Y,MI_all,MI_diff_all)

      ModelName1=modelname+ '_fold'+str(fold_no)+'_epoch_'+str(Noepoch)+'.h5'

      model1=tf.keras.models.load_model(os.path.join(modeldir,ModelName1))

      ypred=model1.predict(X_train)
      ypred_th = (ypred > th).astype(int)

      if gru==1:

        Y = Y[:, 2]
        ypred= ypred[:, 2]
        ypred_th= ypred_th[:, 2]

      # if th==0.5:

      fpr1, tpr1, _ = roc_curve(Y, ypred)
      precision, recall, _ = precision_recall_curve(Y, ypred)
      PR1=auc(recall, precision)
      ROC1=roc_auc_score(Y,ypred)
      fpr.append(fpr1)
      tpr.append(tpr1)
      PR.append(PR1)
      ROC.append(ROC1)

      precision, recall, f1, _ = precision_recall_fscore_support(Y, ypred_th, average='weighted')

      pred.append(list(ypred_th))
      act.append(list(Y))
      fscore.append(f1)
      pred1=np.concatenate(pred,axis=0)
      act1=np.concatenate(act,axis=0)
      cnf_matrix = confusion_matrix(act1, pred1)

      np.save(os.path.join(SaveResults, savenamef1+str(th)),  fscore)
      np.save(os.path.join(SaveResults, cfname+str(th)),  cnf_matrix)

  np.save(os.path.join(SaveResults, fprname),  fpr)
  np.save(os.path.join(SaveResults, tprname),  tpr)
  np.save(os.path.join(SaveResults, prname), PR)
  np.save(os.path.join(SaveResults, rocname),  ROC)


  ####################################plot and save the true vs predicted labels for 3 EDF files##################################
  for j in range(3):
      fold_no=0
      FoldNum=6
      kfold = KFold(n_splits=FoldNum, shuffle=False)

      for trainindx, testindx in kfold.split(range(24)):

        if indx=='test':
          ind=testindx
        else:
          ind=trainindx
        fold_no=fold_no+1
        x, y, mi,mi_diff=ReadMatFiles(dirname,ind,seq_len,diff)

        X_train=Xtrain(cnn,smile,diff,twodcnn,x[j],y[j],mi[j],mi_diff[j])

        ModelName1=modelname+ '_fold'+str(fold_no)+'_epoch_'+str(Noepoch)+'.h5'
        model1=tf.keras.models.load_model(os.path.join(modeldir,ModelName1))

        ypred_plot=model1.predict(X_train)

        if gru==1:

          y = y[j][:, 2]
          ypred_plot= ypred_plot[:, 2]

        else:
          y = y[j]

        plt.subplot(3,2,fold_no)

        plt.plot(range(len(y)), ypred_plot)
        plt.plot(range(len(y)),y)


      plt.suptitle(modelname+'_EDFNo_'+str(j+1)+'_'+indx)

      plt.savefig(SaveResultsTruePred+'/'+modelname+'_EDFNo_'+str(j+1)+'_epoch_'+str(Noepoch)+'_'+indx+'.pdf', format='pdf', bbox_inches = 'tight')
      plt.clf()


  print("--- %s seconds ---" % (time.time() - start_time))
###############################################################Defining parameteres
dirname='/home/baharsalafian/6FoldCrossSMILE'

modeldir='/home/baharsalafian/CNNGRU100_ICASSP'

SaveResults='/home/baharsalafian/ResultsICASSP'

SaveResultsTruePred='/home/baharsalafian/TruePredPlotsICASSP'

ModelTrain(dirname,modeldir,SaveResults,SaveResultsTruePred,'CNNGRU',seq_len=3,cnn=1,smile=0,diff=0,twodcnn=0,indx='test',gru=1,Noepoch=100)
##################
# dirname: directory where dataset is saved i.e. signals, MI estimation and labels
# modeldir: directory where trained models are saved
#SaveResults: directory you wish to save your ResultsICASSP
# SaveResultsTruePred: directory where you wish to save true and predicted labels plots
# 'CNNGRU' : name of the model that you wanna load
# seq_len: refers to the memory length of the data, where in our implementation,for the models with GRU, it is 3 and for CNNs it's 1

# cnn, smile, diff and twodcnn: are control parameters that show which model is being used to get evaluation results, e.g. if you are getting
# the results for a 1D CNN model, the cnn should be set to 1. Therefore, cnn is for 1D CNN, smile for the CNN-SMILE architectures
# and twodcnn for 2D CNN models. diff is for the model that besides MI estimation, the difference of MI between consecutive blocks is also considered as
# additional features

# indx: shows if you are using test or train data to get the evaluation results
# gru: if a model with GRU structure is being used
# Noepoch: number of epochs used during training
