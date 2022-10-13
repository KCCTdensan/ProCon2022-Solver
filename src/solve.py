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
  loop = int((voice_len - 20000) / 100)
  print(loop)
  for i in range(loop):
      i = tf.convert_to_tensor(i, dtype=tf.int64)

      x = voice[start : start + 20000]
      x = np.abs(np.fft.fft(x))
      x = preprocessing.scale(x)
      x = x[:10000]
      x = np.reshape(x,[1,10000,1])
      start += 100

      for p in range(model_n):
          p = tf.convert_to_tensor(p, dtype=tf.int64)

          pre_data = np.round(model[p].predict(x))
          #print(pre_data)
          if pre_data[0][0] == 1:
              ans[p] += 1

  print("pre2_finish")

  print(ans)
  pre_ans = ans

  ans = []
  for i in range(model_n):
      i = tf.convert_to_tensor(i, dtype=tf.int64)

      if i < 44 and pre_ans[i] >= loop - 1:
          str = '{:0=2}'.format((i + 1) % 44)
          if str not in ans:
              ans.append(str)

      elif i >= 44 and pre_ans[i] >= loop - 1:
          str = '{:0=2}'.format((i + 1) % 44)
          if str not in ans:
              ans.append(str)
              
  return ans
