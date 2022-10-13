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

  loop = int(((voice_len - 20000)) / 100)
  if loop > 50:
      loop_list = range(int(loop/2 - 25),int(loop/2 + 25))
      loop = 50
  else:
      loop_list = range(loop)
  print(loop)
  x_list = []

  for i in loop_list:
      i = tf.convert_to_tensor(i, dtype=tf.int64)

      x = voice[i * 100 : i * 100 + 20000]
      x = tf.abs(np.fft.fft(x))
      x = preprocessing.scale(x)
      x = x[:10000]
      x_list.append(x)

  print('problem_load_finish')

  x_list = tf.reshape(x_list,[loop,10000,1])
  for p in range(model_n):
      p = tf.convert_to_tensor(p, dtype=tf.int64)

      pre_data = tf.round(model[p].predict(x_list))
      #print(pre_data)
      for i in range(len(pre_data)):
          if pre_data[i][0] == 1:
              ans[p] += 1

  print('predict_finish')

  print(ans)
  pre_ans = ans

  ans = []
  for i in range(model_n):
      i = tf.convert_to_tensor(i, dtype=tf.int64)

      if i < 44 and pre_ans[i] >= loop - int(loop / 3):
          str = '{:0=2}'.format((i + 1) % 44)
          if str not in ans:
              ans.append(str)

      elif i >= 44 and pre_ans[i] >= loop - int(loop / 3):
          str = '{:0=2}'.format((i) - 43)
          if str not in ans:
              ans.append(str)

  print(ans)

  end = time.time()

  print(f'time ={end - timestart}')

  return ans
