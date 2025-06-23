# SEMGのリアルタイムプロットとCSVファイル保存
#以下ライブラリインポート　なかったら入れる
import serial #これはpyserialというライブラリ　serialライブラリとの競合に注意
import csv
from datetime import datetime

from IPython import get_ipython
get_ipython().magic('reset -sf')

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
from matplotlib.animation import FuncAnimation

plt.close("all")

#%% この区域の変数を変える
t = 30             # サンプリング時間(sec)　任意
period = 0.1          # サンプリング周期(sec) Arduinoとそろえる
title = "name_gu_pa_foreArm"
port = "COM6"         # シリアルポート名　ArduinoIDEから確認できる
baudrate = 115200     # 通信速度 Arduinoに書き込んだ設定と同じにする

#%%Initialise configuration
temp_size = int(t / period)
tf = float(1 / period)

A = np.zeros((temp_size, 2))  # 時間列とデータ列の2次元配列 周期がArduinoと違うとグラフがおかしくなるため注意
times = np.arange(0, t, period)

# シリアル通信初期化
ser = serial.Serial(port, baudrate, timeout=1)

# 保存用ファイル
filename = f"{title}_SamplingTime_{t}_Period_{period}.csv"
csvfile = open(filename, 'w', newline='')
writer = csv.writer(csvfile)

#%% ready for real time plot

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, t)
ax.set_ylim(0, 1024)  # analogReadの範囲（0-1023）
ax.set_xlabel('Time [s]')
ax.set_ylabel('Amplitude')
ax.set_title(f"SEMG Live Plot (Sampling Rate = {tf} Hz)")
ax.grid(True)

data_x = []
data_y = []
index = 0

# 最後にグラフ描くやつ
def on_animation_end():
    csvfile.close()
    plt.figure(2)
    plt.plot(A[:, 0], A[:, 1])
    plt.xlabel('Time [sec]', fontsize=12)
    plt.ylabel('Amplitude', fontsize=12)
    plt.title(f"SEMG Plot (Sampling Rate = {tf} Hz) {title}", fontsize=10)
    plt.grid()
    plt.tight_layout()
    plt.show()

def init():
    line.set_data([], [])
    return line,

def update(frame):
    global index
    if index >= temp_size:
        ani.event_source.stop()
        on_animation_end()  #アニメーション終了後にグラフ描画
        return line,

    try:
        line_raw = ser.readline().decode().strip()
        print(line_raw)
        #ser.write(bytes([123])) #Arduinoに変数を送るときはコメントアウトを外す csvファイルへの書き込みも無効化しておく
        if line_raw:
            value = int(line_raw)
            time_point = index * period

            data_x.append(time_point)
            data_y.append(value)

            A[index, 0] = time_point
            A[index, 1] = value

            writer.writerow([time_point, value])
            line.set_data(data_x, data_y)
            index += 1
    except:
        pass

    return line,

ani = FuncAnimation(fig, update, init_func=init, interval=period * 1000, blit=True)
plt.show()

ser.close() #シリアルポート開放