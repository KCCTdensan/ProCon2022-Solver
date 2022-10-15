from sklearn import preprocessing
from tensorflow.python.keras.models import load_model
import tensorflow as tf
import numpy as np
import librosa

voice_len = 3000

model = []
model_light = []
model_judge = []
model_n = 88

def initModel():
  model_judge.append(load_model(f'./train/voice_judge.h5'))
  for i in range(model_n):
    i = tf.convert_to_tensor(i, dtype=tf.int64)
    models = load_model(f'./train/voice_correct_in{i}.h5')
    light_models = load_model(f'./train_l/voice_correct_in{i}_light.h5')
    model.append(models)
    model_light.append(light_models)
  print("model loaded")

async def solve(f,stack_num):
  voice, sr = librosa.load(f,sr=48000)
  voice_len = len(voice)

  loop = int((voice_len - 20000) / 100)
  loop = 20

  x_list = []
  for i in range(loop):
    i = tf.convert_to_tensor(i, dtype=tf.int64)

    x = voice[i * 100 : i * 100 + 20000]
    x = tf.abs(np.fft.fft(x))
    x = preprocessing.scale(x)
    x = x[:10000]
    x_list.append(x)

  x_list = tf.reshape(x_list,[loop,10000,1])
  print('problem_load_finish')

  ans_judge = np.zeros(3)
  pre_judge = tf.round(model_judge[0].predict(x_list))
  for i in range(len(pre_judge)):
    if pre_judge[i][0] == 1:
      ans_judge[0] += 1
    elif pre_judge[i][1] == 1:
      ans_judge[1] += 1
    elif pre_judge[i][2] == 1:
      ans_judge[2] += 1

  if ans_judge[0] > ans_judge[1] and ans_judge[0] > ans_judge[2]:
    leng = range(0,44)
  elif ans_judge[1] > ans_judge[0] and ans_judge[1] > ans_judge[2]:
    leng = range(0,88)
  elif ans_judge[2] > ans_judge[0] and ans_judge[2] > ans_judge[1]:
    leng = range(44,88)
  print(leng)

  ans = np.zeros(model_n)
  for p in leng:
    p = tf.convert_to_tensor(p, dtype=tf.int64)

    if stack_num > 8:
      pre_data = tf.round(model[p].predict(x_list))
    else:
      pre_data = tf.round(model_light[p].predict(x_list))
    #print(pre_data)
    for i in range(len(pre_data)):
      if pre_data[i][0] == 1:
        ans[p] += 1

  print('predict_finish')

  str_len = []
  for i in range(88):
    str_len.append(str(i+1))

  d = zip(str_len, ans)
  d.sort(key=lambda x: x[1], reverse=True)
  print(d)

  print(ans)
  pre_ans = ans
  ans = []
  for i in leng:
    i = tf.convert_to_tensor(i, dtype=tf.int64)

    if i < 44 and pre_ans[i] >= loop - int(loop / 10):
      str_l = '{:0=2}'.format((i + 1) % 44)
      if str_l not in ans:
        ans.append(str_l)

    elif i >= 44 and pre_ans[i] >= loop - int(loop / 10):
      str_l = '{:0=2}'.format((i) - 43)
      if str_l not in ans:
        ans.append(str_l)

  print(ans)

  return ans
