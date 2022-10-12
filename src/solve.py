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
  voice, sr = librosa.load(f,sr=48000)
  voice_len = len(voice)
  ans = np.zeros(model_n)

  start = 0
  for i in range(10):

    x = voice[start : start + 20000]
    x = np.abs(np.fft.fft(x))
    x = preprocessing.scale(x)
    start += 100

    for p in range(model_n):
      pre_data = np.round(model[i].predict(voice))
      if pre_data[0] == 1:
        ans[p] += 1

  end = voice_len - (voice_len % 100)
  for i in range(10):

    x = voice[end - 20000 : end]
    x = np.abs(np.fft.fft(x))
    x = preprocessing.scale(x)
    end -= 100

    for p in range(model_n):
      pre_data = np.round(model[i].predict(voice))
      if pre_data[0] == 1:
        ans[p] += 1

  ans = np.empty(0)
  for i in range(model_n):
    if i < 44 and ans[i] >= 14:
      str = '{:0=2}'.format((i + 1) % 44)
      if str not in ans:
        ans = np.append(ans,str)

    elif i >= 44 and ans[i] >= 14:
      str = '{:0=2}'.format((i + 1) % 44)
      if str not in ans:
        ans = np.append(ans,str)

  return ans
