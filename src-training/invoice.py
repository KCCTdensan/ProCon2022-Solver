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

    for i in range(nb_training):
        print(i)
        mix = random.randint(3,10)
        x = np.zeros(max_len)
        y = np.zeros(nb_voice)

        num = 0
        if random.randint(0,1) == 1:
            y[voice_num] = 1
        while num < mix:
            ran_num = random.randint(0,nb_voice - 1)
            if y[ran_num] == 0:
                y[ran_num] = 1
                num += 1

        #print(y)
        len_max = 0
        min_len = 0
        for p in range(nb_voice):
            if y[p] == 1:
                if p < 44:
                    num = p + 1
                    path = './JKSpeech/J{:0=2}.wav'.format(num)
                    voice,sr =  librosa.load(path)
                    if(p == voice_num):
                        min_len = len(voice)
                    if(len(voice) > len_max):
                        len_max = len(voice)

                else:
                    num = p - 43
                    path = './JKSpeech/E{:0=2}.wav'.format(num)
                    voice,sr = librosa.load(path)
                    if(p == voice_num):
                        min_len = len(voice)
                    if(len(voice) > len_max):
                        len_max = len(voice)

                dif = random.choice(dif_nom)
                zeros = np.zeros(max_len - len(voice) + dif)
                voice = np.append(voice[dif:],zeros)
                x += voice

        ans = 0
        mode = 0
        for p in range(len(y)):
            if y[voice_num] == 1:
                mode = 1
                ans = [1,0]
                ran_len = random.randint(0,int(min_len - 10000))
                break
            else:
                ans = [0,1]

        if(mode == 0):
            ran_len = random.randint(0,(len_max-10000))

        x = x[ran_len:(ran_len + 10000)]
        x = np.abs(np.fft.fft(x))
        x = preprocessing.scale(x)

        data_x = np.append(data_x,x)
        data_y = np.append(data_y,ans)

        if((i + 1) % 100  == 0):
            print(f'training:{i+1}')

    data_x = np.reshape(data_x,[nb_training,10000,1])
    data_y = np.reshape(data_y,[nb_training,2])

    print('u')

    print(data_x)
    print(data_y)

    return data_x,data_y