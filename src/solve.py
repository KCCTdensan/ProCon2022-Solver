#!/usr/bin/env python3

from sklearn import preprocessing
from tensorflow.python.keras.models import load_model
import numpy as np
import random
import librosa
import os

voice_len = 3000

def solve(path):

  model = []
  for i in range(88):
    model.append(load_model(f'voice_correct_in{voice_num}.h5')) #main.pyが始まった瞬間にこれを読み込みたい

  with open(path) as file:

    voice,sr =  librosa.load(path)
    voice = voice[:10000]
    voice = np.abs(np.fft.fft(voice))
    voice = preprocessing.scale(voice)
    voice = voice[:voice_len]
    voice = np.reshape(voice,[1,voice_len,1])

    ans = np.empty(0)
    for i in range(88):

      pre_data = np.round(model[i].predict(voice))
      
      str = '{:0=2}'.format((i + 1) % 44)
      if pre_data[0] == 1 and  (str in ans) == False:
        ans = np.append(ans,str)

    return []
