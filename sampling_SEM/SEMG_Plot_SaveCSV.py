#リアルタイムプロットなしのシンプルなバージョン(グラフ描画とcsvファイル出力のみ)
import serial
import csv
from datetime import datetime

from IPython import get_ipython
get_ipython().magic('reset -sf')

# いつものライブラリインポート
import numpy as np
import matplotlib.pyplot as plt

# 信号処理のライブラリ
from scipy import signal
import pandas as pd

from matplotlib.animation import FuncAnimation

#図の軸をクリア
#plt.cla()

#図をクリア
#plt.clf()

#図ウィンドウを閉じる
plt.close("all")




#%%この区域の変数を変える あとは変えない
#サンプリング時間(sec) 
t = 10
#サンプリング周期(sec) Arduino側のdelya(period)と同期させること　単位に注意
period = 0.1
#CSVファイル名
title = "test_saved_csv"
#%%



#サンプリング数
temp_size = int((t/period))

#サンプリングレート（サンプリング周波数）
tf = float(1/period)

temp=np.zeros(temp_size)
temp=np.array([temp]).T

A = np.arange(0,t, period) #時間関数
A=np.array([A]).T

#サンプリング数を求めて、その間だけwhileを回す
# Arduinoのシリアルポートを指定（例: Windowsなら "COM3", macなら "/dev/ttyUSB0"）
ser = serial.Serial('COM6', 115200)

# ファイル名にタイムスタンプを付ける
#filename = f"arduino_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
filename = f"{title}_SamplingTime_{t}_Period_{period}.csv"

with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(temp_size):
        line = ser.readline().decode().strip()  # 1行読み込み
        print(line)
        #line = line.strip()
        temp[i, 0] = int(line)
        if line:
            writer.writerow(line.split(','))    # CSVの行として保存

            
#グラフ描画用
A=np.hstack([A,temp])

plt.figure(1)
plt.plot(A[:,0],A[:,1])

#plt.legend(bbox_to_anchor=(1, 0), loc='lower right', borderaxespad=1, ncol=2, fontsize=100)
#plt.legend()
plt.xlabel('Time[sec]',fontsize=12)
plt.ylabel('Amplitude',fontsize=12)



plt.title(f"SEMG plot (sampling late = {tf} Hz)", fontsize=15)
plt.grid()
plt.show()
            
ser.close()