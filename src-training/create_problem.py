#!/usr/bin/env python3
from multiprocessing import Pool, cpu_count
from sklearn import preprocessing
import numpy as np
import random
import librosa
import os

# loops: 500*n
def create(loops:int):

    nb_voice = 88
    max_len = 185000
    dif_nom = np.arange(0,10000,100)
    problem_len = 10000
    nb_training = 500
    voice_num = _voice_num

    data_arr = np.empty(0)
    len_arr = np.empty(0)

    # os.remove('./data/data_x.csv')
    # os.remove('./data/data_y.csv')

    for i in range(nb_voice):
        if i < 44:
            num = i + 1
            path = './JKspeech/J{:0=2}.wav'.format(num)
            voice,sr =  librosa.load(path)
            len_arr = np.append(len_arr,len(voice))
            zeros = np.zeros(max_len - len(voice))
            voice = np.append(voice,zeros)
            data_arr = np.append(data_arr,voice)

        else:
            num = i - 43
            path = './JKspeech/E{:0=2}.wav'.format(num)
            voice,sr = librosa.load(path)
            len_arr = np.append(len_arr,len(voice))
            zeros = np.zeros(max_len - len(voice))
            voice = np.append(voice,zeros)
            data_arr = np.append(data_arr,voice)

    data_arr = np.reshape(data_arr,[nb_voice, max_len])
    print(data_arr)
    print(len_arr)

    with open('./data/data_x.csv', 'a') as f_x:
        with open('./data/data_y.csv', 'a') as f_y:
            for j in range(loops):

                data_x = np.empty(0)
                data_y = np.empty(0)

                for i in range(nb_training):

                    mix = random.randint(3,20)
                    x = np.zeros(problem_len)
                    y = np.zeros(nb_voice)

                    num = 0
                    while num < mix:
                        ran_num = random.randint(0,nb_voice - 1)
                        if y[ran_num] == 0:
                            y[ran_num] = 1
                            num += 1

                    voice_max = 0
                    for p in range(nb_voice):
                        if len_arr[p] > voice_max and y[ran_num] == 1:
                            voice_max = len_arr[p]

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
                    data_y = np.append(data_y,y)

                    if (i+1) % 100 == 0:
                        print(f"training : {i+1}")

                print(f"file writing{j}")
                np.savetxt(f_x,data_x,delimiter=",")
                np.savetxt(f_y,data_y,delimiter=",")
