#!/usr/bin/env python3

from sklearn import preprocessing
import numpy as np
import random
import librosa

nb_voice = 88
max_len = 185000
dif_nom = np.arange(0,10000,100)

def Create_problem(nb_training,voice_num):

    data_x = np.empty(0)
    data_y = np.empty(0)

    data_arr = np.empty(0)
    len_arr = np.empty(0)

    for i in range(nb_voice):
        if i < 44:
            num = i + 1
            path = './JKSpeech/J{:0=2}.wav'.format(num)
            voice,sr =  librosa.load(path)
            zeros = np.zeros(max_len - len(voice))
            voice = np.append(voice,zeros)
            len_arr = np.append(len_arr,len(voice))
            data_arr = np.append(len_arr,voice)

        else:
            num = i - 43
            path = './JKSpeech/E{:0=2}.wav'.format(num)
            voice,sr = librosa.load(path)
            zeros = np.zeros(max_len - len(voice))
            voice = np.append(voice,zeros)
            len_arr = np.append(len_arr,len(voice))
            data_arr = np.append(len_arr,voice)

        print(f'{i} import end.')

    data_arr = np.reshape(data_arr,[max_len,nb_voice])

    for i in range(nb_training):

        mix = random.randint(3,20)
        x = np.zeros(10000)
        y = np.zeros(nb_voice)

        num = 0
        if random.randint(0,1) == 1:
            y[voice_num] = 1

        while num < mix:
            ran_num = random.randint(0,nb_voice - 1)
            if y[ran_num] == 0:
                y[ran_num] = 1
                num += 1

        voice_max = 0
        for p in range(nb_voice):
            if len_arr[p] > voice_max:
                voice_max = len_arr[p]
        
        ans = [0,1]
        if y[voice_num] == 1:
            ans = [1,0]

        if ans[0] == 1:
            voice_max = len_arr[voice_num]
    
        for p in range(nb_voice):
            loc = random.randint(0,int(voice_max - 10000))
            if y[p] == 1:
                dif = random.choice(dif_nom)
                x += data_arr[dif + loc:dif + loc + 10000]

        data_x = np.append(data_x,x)
        data_y = np.append(data_y,ans)

        if i % 100 == 0:
            print(f"training : {i}")

    data_x = np.reshape(data_x,[nb_training,10000,1])
    data_y = np.reshape(data_y,[nb_training,2])

    print(data_x)
    print(data_y)

    return data_x,data_y