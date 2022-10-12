#!/usr/bin/env python3

import os

#os.add_dll_directory(os.path.join(os.environ['CUDA_PATH'], 'bin'))

import tensorflow as tf

gpus = tf.config.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
logical_gpus = tf.config.list_logical_devices("GPU")
print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")

tf.debugging.set_log_device_placement(True)
strategy = tf.distribute.MirroredStrategy(logical_gpus)

from keras.models import Sequential,Model
from keras.layers import *
from keras.callbacks import EarlyStopping,LearningRateScheduler
from keras.optimizers import Adam,RMSprop
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import keras.backend as K
import numpy as np
import create_problem
import gc

os.environ['TF_ENABLE_GPU_GARBAGE_COLLECTION']='false'

np.set_printoptions(edgeitems=10)

max_voice_len = 95000
data_x = np.empty(0)
data_y = np.empty(0)
nb_training = 100000
problem_len = 10000
nb_voice = 88

def step_decay(epoch):
    lr = 0.003
    if(epoch >= 3):
        lr/=5
    if(epoch>=10):
        lr/=2
    return lr

for i in range(44,88):
    print(f'\nvoice_num = {i}')

    data_x,data_y = create_problem.create(nb_training,i)

    data_x = np.reshape(data_x,[nb_training,problem_len,1])
    data_y = np.reshape(data_y,[nb_training,nb_voice])

    ans = np.empty(0)
    for p in range(nb_training):
        if data_y[p][i] == 1:
            ans = np.append(ans,[1,0])
        else:
            ans = np.append(ans,[0,1])
    
    ans = np.reshape(ans,[nb_training,2])
    #print(f'\nans = {ans}')
    print(type(data_x))
    print(type(data_y))

    x_train, x_valid, y_train, y_valid = train_test_split(data_x, ans, test_size=0.25, shuffle= True)

    Input_shape = np.shape(x_train)[1:]

    def get_model():
        with strategy.scope():

            model = Sequential()
            model.add(Conv1D(128, 4, activation='relu',input_shape=Input_shape))
            model.add(MaxPool1D(pool_size=2, padding='same'))
            model.add(Conv1D(64, 4, activation='relu'))
            model.add(MaxPool1D(pool_size=2, padding='same'))
            model.add(Conv1D(32, 4, activation='relu'))
            model.add(MaxPool1D(pool_size=2, padding='same'))
            model.add(LSTM(16, return_sequences=True))
            model.add(Flatten())
            model.add(Dense(2,activation='softmax'))
            model.compile(loss="binary_crossentropy", optimizer=Adam(lr=3e-3),metrics=['accuracy'])

            return model

    model = get_model()

    model.summary()

    early_stopping =  EarlyStopping(monitor='val_loss',min_delta=0.0,patience=3)

    lr_decay = LearningRateScheduler(step_decay)
    history = model.fit(x_train, y_train, batch_size=128, epochs=20,verbose=1,validation_data=(x_valid, y_valid),callbacks=[early_stopping,lr_decay])

    plt.plot(history.epoch, history.history["accuracy"], label="Train accracy")
    plt.plot(history.epoch, history.history["val_accuracy"], label="Validation accracy")
    plt.xlabel("epoch")
    plt.legend()
    
    plt.savefig(f"train/voice_correct_in{i}.png")
    model.save(f"train/voice_correct_in{i}.h5")

    K.clear_session()
    gc.collect()
    plt.clf()
