from sklearn import preprocessing
from tensorflow.python.keras.models import load_model
import numpy as np
import librosa

voice_len = 3000

model = []
model_n = 88

def initModel():
  return #
  for i in range(model_n):
    model.append(load_model(f'voice_correct_in{i}.h5'))
  print("model loaded")

def solve(f):
  voice, sr = librosa.load(f)
  voice = voice[:10000]
  voice = np.abs(np.fft.fft(voice))
  voice = preprocessing.scale(voice)
  voice = voice[:voice_len]
  voice = np.reshape(voice, [1, voice_len, 1])

  ans = np.empty(0)
  for i in range(model_n):
    pre_data = np.round(model[i].predict(voice))
    str = '{:0=2}'.format((i + 1) % 44)
    if pre_data[0] == 1 and not str in ans:
      ans = np.append(ans,str)

  return []
