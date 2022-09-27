#!/usr/bin/env python3

import os
os.add_dll_directory(os.path.join(os.environ['CUDA_PATH'], 'bin'))

import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpus[0], True)

from keras.models import Model,Sequential
from keras.layers import *
from keras import callbacks
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import create_problem
import invoice


os.environ['TF_ENABLE_GPU_GARBAGE_COLLECTION']='false'

max_voice_len = 95000
data_x = np.empty(0)
data_y = np.empty(0)
nb_training = 10000
nb_voice = 88
voice_num = 0

data_x,data_y = invoice.Create_problem(nb_training,voice_num)

x_train, x_valid, y_train, y_valid = train_test_split(data_x, data_y, test_size=0.2, shuffle= True)

Input_shape = x_train.shape[1:]

model = Sequential()
model = Sequential()
model.add(Conv1D(128, 32, activation='relu',input_shape=Input_shape))
model.add(MaxPool1D(pool_size=2, padding='same'))
model.add(Dense(64,activation='relu'))
model.add(Dense(16,activation='relu'))
model.add(Flatten())
model.add(Dense(2,activation='softmax'))
model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=1e-5),metrics=['accuracy'])

model.summary()

history = model.fit(x_train, y_train, batch_size=64, epochs=100,verbose=1,validation_data=(x_valid, y_valid))

plt.plot(history.epoch, history.history["accuracy"], label="Train accracy")
plt.plot(history.epoch, history.history["val_accuracy"], label="Validation accracy")
plt.xlabel("epoch")
plt.legend()
plt.show()

model.save(f'voice_correct_in{voice_num}.h5')