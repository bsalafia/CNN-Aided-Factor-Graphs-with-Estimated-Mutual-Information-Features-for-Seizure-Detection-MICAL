# -*- coding: utf-8 -*-
"""CNNSMILEGRU_Bs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10HugrJofKv4UU3ELsSVpZFUZtU_8Ig97
"""

import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="7"
import tensorflow as tf
import scipy
import h5py
import glob, os
from scipy.io import loadmat

from keras.models import Model
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline
# from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten,TimeDistributed, GRU,Concatenate
from keras.optimizers import Adam
from keras.layers.normalization import BatchNormalization
from keras.utils import np_utils
from keras.layers import Conv1D, GlobalAveragePooling1D,MaxPooling1D
from keras.layers.advanced_activations import LeakyReLU
from keras.preprocessing.image import ImageDataGenerator
from sklearn import preprocessing
from keras import regularizers
from numpy import mean
from numpy import std
from tqdm.auto import tqdm
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from tensorflow.keras.datasets import cifar10
from keras.optimizers import Adam
from keras.layers.normalization import BatchNormalization
from keras.utils import np_utils
from keras.layers import Conv1D, MaxPooling1D, ZeroPadding1D, GlobalAveragePooling1D,Bidirectional
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
import time
import gc
# from google.colab import drive
# drive.mount('/content/drive')

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

def  Conv_BN_Act_Pool(filtNo,filtsize1,filtsize2,input1,activation,PoolSize):
    conv1 = Conv1D(filtNo,filtsize1)(input1)
    conv2 = Conv1D(filtNo, filtsize2)(conv1)
    BN=BatchNormalization(axis=-1)(conv2)
    ActFunc=Activation(activation)(BN)
    pool1=MaxPooling1D(pool_size=PoolSize)(ActFunc)

    return pool1

def define_model_CNNSMILEGRU():

  denseSize=8
  activation='relu'
  filtsize1=22
  filtNo1=8
  filtsize2=10
  filtNo2=16
  PoolSize=2
  ##################
  memory=3
  vectorsize=18
  input_shape=(1024,18)
  input_shape_GRU=(memory,1024,18)
  dim_data =int(vectorsize*(vectorsize+1)/2)-18
  input1 = Input(input_shape)
  input1GRU=Input(input_shape_GRU)
  input2GRU= Input((memory,dim_data,))

  model1=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,input1,activation,PoolSize)
  model2=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model1,activation,PoolSize)
  model3=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model2,activation,PoolSize)
  model4=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model3,activation,PoolSize)
  model5=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model4,activation,PoolSize)
  conv6=Conv1D(filtNo1,1)(model5)
  drop1=Dropout(0.25)(conv6)
  flat=Flatten()(drop1)
  # dense=Dense(denseSize)(flat)
##################################################################

  vector_input = Input((dim_data,))
  # Concatenate the convolutional features and the vector input
  concat_layer = Concatenate()([flat,vector_input])

  cnn = Model(inputs=[input1, vector_input], outputs=concat_layer)

  encoded_frames = TimeDistributed(cnn)([input1GRU,input2GRU])
  encoded_sequence = Bidirectional(GRU(50, return_sequences=True))(encoded_frames)
  output=TimeDistributed(Dense(1,activation='sigmoid'))(encoded_sequence)

  model = Model(inputs=[input1GRU,input2GRU], outputs=output)
  model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

  return model

def define_model_CNNSMILEDiffGRU():


  denseSize=8
  activation='relu'
  filtsize1=22
  filtNo1=8
  filtsize2=10
  filtNo2=16
  PoolSize=2
  ##################
  memory=3
  vectorsize=18
  input_shape=(1024,18)
  input_shape_GRU=(memory,1024,18)
  dim_data =int(vectorsize*(vectorsize+1)/2)-18
  input1 = Input(input_shape)
  input1GRU=Input(input_shape_GRU)
  input2GRU= Input((memory,dim_data,))
  input3GRU= Input((memory,dim_data,))

  model1=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,input1,activation,PoolSize)
  model2=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model1,activation,PoolSize)
  model3=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model2,activation,PoolSize)
  model4=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model3,activation,PoolSize)
  model5=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model4,activation,PoolSize)
  conv6=Conv1D(filtNo1,1)(model5)
  drop1=Dropout(0.25)(conv6)
  flat=Flatten()(drop1)
  # dense=Dense(denseSize)(flat)
##################################################################

  vector_input1 = Input((dim_data,))
  vector_input2=Input((dim_data,))
  # Concatenate the convolutional features and the vector input
  concat_layer= Concatenate()([flat,vector_input1,vector_input2])

  # define a model with a list of two inputs
  cnn = Model(inputs=[input1, vector_input1,vector_input2], outputs=concat_layer)

  encoded_frames = TimeDistributed(cnn)([input1GRU,input2GRU,input3GRU])
  encoded_sequence = Bidirectional(GRU(50, return_sequences=True))(encoded_frames)
  output=TimeDistributed(Dense(1,activation='sigmoid'))(encoded_sequence)

  model = Model(inputs=[input1GRU,input2GRU,input3GRU], outputs=output)
  model.compile(optimizer=Adam(learning_rate=0.001),loss='binary_crossentropy', metrics=['accuracy'])

  return model

def define_model_CNNGRU():

  memory=3
  vectorsize=18
  input_shape=(1024,18)
  input_shape_GRU=(memory,1024,18)
  denseSize=8
  activation='relu'
  filtsize1=22
  filtNo1=8
  filtsize2=10
  filtNo2=16
  PoolSize=2
  input1 = Input(input_shape)
  inputGRU=Input(input_shape_GRU)
  model1=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,input1,activation,PoolSize)
  model2=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model1,activation,PoolSize)
  model3=Conv_BN_Act_Pool(filtNo1,filtsize2,filtsize1,model2,activation,PoolSize)
  model4=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model3,activation,PoolSize)
  model5=Conv_BN_Act_Pool(filtNo2,filtsize2,filtsize1,model4,activation,PoolSize)
  conv6=Conv1D(filtNo1,1)(model5)
  drop1=Dropout(0.25)(conv6)
  flat=Flatten()(drop1)
  cnn=Model(inputs=input1,outputs=flat)
  encoded_frames = TimeDistributed(cnn)(inputGRU)
  encoded_sequence = Bidirectional(GRU(50, return_sequences=True))(encoded_frames)
  output=TimeDistributed(Dense(1,activation='sigmoid'))(encoded_sequence)

  model = Model(inputs=inputGRU, outputs=output)
  model.compile(optimizer=Adam(learning_rate=0.001),loss='binary_crossentropy', metrics=['accuracy'])
  return model

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
      # print(x.shape)
      # print(real_y.shape)
      # print(MI.shape)

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


  X=np.concatenate(X,axis=0)
  Y=np.concatenate(Y,axis=0)
  MI_all=np.concatenate(MI_all,axis=0)
  MI_diff_all=np.concatenate(MI_diff_all,axis=0)

  print(X.shape)
  print(Y.shape)
  print(MI_all.shape)
  print(MI_diff_all.shape)

  return X, Y, MI_all, MI_diff_all

def ModelTrain(dirname,SaveResults,modelname,seq_len,cnn,smile,diff):

  FoldNum=6
  kfold = KFold(n_splits=FoldNum, shuffle=False)
  start_time = time.time()
  fold_no=1
  for trainindx, testindx in kfold.split(range(24)):

    batchsize=256
    epoch=100


    x, y, mi,mi_diff=ReadMatFiles(dirname,trainindx,seq_len,diff)

    if cnn==1:

      tf.keras.backend.clear_session()
      model=define_model_CNNGRU()
      X_train=x

    if smile==1:
      tf.keras.backend.clear_session()
      model=define_model_CNNSMILEGRU()
      print(str(define_model_CNNSMILEGRU))
      X_train=[x,mi]

    if diff==1:

      tf.keras.backend.clear_session()
      model=define_model_CNNSMILEDiffGRU()
      X_train=[x,mi,mi_diff]



    ##################################################################
    from sklearn.utils import class_weight
    cw = class_weight.compute_class_weight('balanced', np.unique(y),np.ravel(y))
    sample_weight = np.zeros_like(y)
    sample_weight[y == 0] = cw[0]
    sample_weight[y == 1] = cw[1]

  # print(y)
    # print(sample_weight)
    his= tf.keras.callbacks.History()
    history=model.fit(X_train, y, validation_split=0, batch_size=batchsize, epochs=epoch, sample_weight=sample_weight, verbose = 2)
    #
    X_train = None
    Y_train = None
    gc.collect()


    model.save(SaveResults+'/'+modelname+'_fold'+str(fold_no)+'_epoch_'+str(epoch)+'.h5')

    # print(history)
    print(history.history['loss'])
    # plt.plot(history.history['loss'])
    # plt.plot(history.history['accuracy'])
    # plt.title(modelname+'_fold'+str(fold_no)+'_epoch_'+str(epoch))
    # plt.legend(['loss', 'accuracy'], loc='upper left')
    # plt.ylabel('%')
    # plt.xlabel('epoch')
    #
    #
    # plt.savefig(SaveResults+'/'+'history_'+modelname+'_fold'+str(fold_no)+'_epoch_'+str(epoch)+'.pdf', format='pdf', bbox_inches = 'tight')
    # plt.clf()
    fold_no=fold_no+1
    tf.keras.backend.clear_session()
  print("--- %s seconds ---" % (time.time() - start_time))

dirname='/home/baharsalafian/6FoldCrossSMILE'

SaveResults='/home/baharsalafian/CNNGRU100_ICASSP'
# seq_len=7
ModelTrain(dirname,SaveResults,'CNNGRU',seq_len=3,cnn=1,smile=0,diff=0)

## dirname: data directory
## SaveResults: Save directory
## 'CNNSMILEDiffGRU' : name of the model you wanna save
## cnn: if you wanna run 1d cnn, smile for cnn-smile
# seq_len: refers to the memory length of the data, where in our implementation,for the models with GRU, it is 3 and for CNNs it's 1
