#!/usr/bin/env python3

import os
from multiprocessing import cpu_count
import tensorflow as tf
import numpy as np

##
## config
##

nb_training = 10000
nb_voice = 88
max_voice_len = 95000
voice_num = 0

## https://www.tensorflow.org/guide/gpu?hl=ja

os.environ["TF_ENABLE_GPU_GARBAGE_COLLECTION"] = "false"

## multiple cores

## こんなことしなくても自動でスレッド数は調節してくれるらしい
## https://www.tensorflow.org/api_docs/python/tf/config/threading
## https://stackoverflow.com/questions/63336300/tensorflow-2-0-utilize-all-cpu-cores-100
# num_threads = cpu_count()
# tf.config.threading.set_inter_op_parallelism_threads(num_threads)
# tf.config.threading.set_intra_op_parallelism_threads(num_threads)
# print(num_threads, "threads")

## multiple GPUs

## https://www.tensorflow.org/guide/gpu#tfdistributestrategy%E3%82%92%E4%BD%BF%E7%94%A8%E3%81%99%E3%82%8B
gpus = tf.config.list_physical_devices("GPU")
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
logical_gpus = tf.config.list_logical_devices("GPU")
print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")

tf.debugging.set_log_device_placement(True)
strategy = tf.distribute.MirroredStrategy(logical_gpus)

##
## main
##

from keras.models import Model, Sequential
from keras.layers import *
from keras import callbacks
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import invoice

data_x = np.empty(0)
data_y = np.empty(0)
data_x, data_y = invoice.Create_problem(nb_training, voice_num)

x_train, x_valid, y_train, y_valid = train_test_split(
    data_x, data_y, test_size=0.2, shuffle=True
)

Input_shape = x_train.shape[1:]

## https://www.tensorflow.org/tutorials/distribute/save_and_load
def get_model():
    with strategy.scope():
        model = Sequential()
        model.add(Conv1D(128, 32, activation="relu", input_shape=Input_shape))
        model.add(MaxPool1D(pool_size=2, padding="same"))
        model.add(Dense(64, activation="relu"))
        model.add(Dense(16, activation="relu"))
        model.add(Flatten())
        model.add(Dense(2, activation="softmax"))
        model.compile(
            loss="categorical_crossentropy",
            optimizer=Adam(lr=1e-5),
            metrics=["accuracy"],
        )
        return model


model = get_model()

model.summary()

history = model.fit(
    x_train,
    y_train,
    batch_size=64,
    epochs=100,
    verbose=1,
    validation_data=(x_valid, y_valid),
)

##
## dist
##

plt.plot(history.epoch, history.history["accuracy"], label="Train accracy")
plt.plot(history.epoch, history.history["val_accuracy"], label="Validation accracy")
plt.xlabel("epoch")
plt.legend()
plt.show()

model.save(f"train/voice_correct_in{voice_num}.h5")
