#!/usr/bin/env python3

from sklearn import preprocessing
import numpy as np
import random
import librosa

nb_voice = 88
max_len = 185000
dif_nom = np.arange(0,10000,100)
problem_len = 10000
nb_training = 10000
voice_num = 0

data_x = np.empty(0)
data_y = np.empty(0)

data_arr = np.empty(0)
len_arr = np.empty(0)

for i in range(nb_voice):
    if i < 44:
        num = i + 1
        path = './JKSpeech/J{:0=2}.wav'.format(num)
        voice,sr =  librosa.load(path)
        len_arr = np.append(len_arr,len(voice))
        zeros = np.zeros(max_len - len(voice))
        voice = np.append(voice,zeros)
        data_arr = np.append(data_arr,voice)

    else:
        num = i - 43
        path = './JKSpeech/E{:0=2}.wav'.format(num)
        voice,sr = librosa.load(path)
        len_arr = np.append(len_arr,len(voice))
        zeros = np.zeros(max_len - len(voice))
        voice = np.append(voice,zeros)
        data_arr = np.append(data_arr,voice)

data_arr = np.reshape(data_arr,[nb_voice, max_len])
print(data_arr)
print(len_arr)

for i in range(nb_training):

    mix = random.randint(3,19)
    x = np.zeros(problem_len)
    y = np.zeros(nb_voice)

    num = 0
    y[voice_num] = random.randint(0,1)

    while num < mix:
        ran_num = random.randint(0,nb_voice - 1)
        if y[ran_num] == 0:
            y[ran_num] = 1
            num += 1

    voice_max = 0
    for p in range(nb_voice):
        if len_arr[p] > voice_max and y[ran_num] == 1:
            voice_max = len_arr[p]
    
    ans = [0,1]
    if y[voice_num] == 1:
        ans = [1,0]

    if ans[0] == 1:
        voice_max = len_arr[voice_num]

    dif_arr = np.empty(0)
    dif_max = 0
    for p in range(nb_voice):
        if y[p] == 1:
            dif = random.choice(dif_nom)
            dif_arr = np.append(dif_arr,dif)
            if(dif_max < dif):
                dif_max = dif

    loc = random.randint(0,int(voice_max - (problem_len + dif_max)))
    num = 0
    for p in range(nb_voice):
        if y[p] == 1:
            x += data_arr[p][int(dif_arr[num] + loc):int(dif_arr[num] + loc + problem_len)]
            num += 1

    x = np.abs(np.fft.fft(x))
    x = preprocessing.scale(x)
    data_x = np.append(data_x,x)
    data_y = np.append(data_y,ans)

    if i % 100 == 0:
        print(f"training : {i}")

data_x = np.reshape(data_x,[nb_training,problem_len])
data_y = np.reshape(data_y,[nb_training,2])

np.savetxt("./data/data_x.csv", data_x, delimiter=",")
np.savetxt("./data/data_y.csv", data_y, delimiter=",")