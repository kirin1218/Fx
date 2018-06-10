import os
#import datetime as dt
#import matplotlib.pyplot as plt
import numpy as np

def MakeSMA(lists,timelists=None,term=10):
    retList =[]
    size = len(lists)
    for i in range(size):
        if i >= term-1:
            invalid = False
            if timelists is not None:
                nowtime = timelists[i]
            sum = 0
            for j in range(term):
                if timelists is not None:
                    curtime = timelists[i-j]
                    if nowtime >= curtime:
                        diff = nowtime - curtime
                    else:
                        diff = nowtime+60 - curtime
                    if diff != j:
                        invalid = True
                        break
                sum += lists[i-j]
            if invalid == False:
                retList.append(sum/term)
            else:
                retList.append(0.)
        else:
            retList.append(0.)
    return retList

def MakeEMA(lists,timelists=None,term=10):
    retList =[]
    size = len(lists)
    for i in range(size):
        if i >= term-1:
            invalid = False
            if timelists is not None:
                nowtime = timelists[i]
            sum = lists[i]
            for j in range(term):
                if timelists is not None:
                    curtime = timelists[i-j]
                    if nowtime >= curtime:
                        diff = nowtime - curtime
                    else:
                        diff = nowtime+60 - curtime
                    if diff != j:
                        invalid = True
                        break
                sum += lists[i-j]
            if invalid == False:
                retList.append(sum/(term+1))
            else:
                retList.append(0.)
        else:
            retList.append(0.)
    return retList

#MACD＝短期EMA-長期EMA(短期と長期のEMAの乖離幅)
#シグナル＝MACDの指数平滑移動平均線
#(通常用いる期間：短期12日、長期26日、シグナル9日)
#≪指数平滑移動平均線(EMA：Exponential Moving Average)の計算式≫
#MACDの計算式
#当日の指数平滑平均＝前日の指数平滑平均＋α×（当日の終値-前日の指数平滑平均）
#α＝2/(n+1)
#n:初日の単純平均の期間
#※初日は単純平均を使う
def MakeMACD(lists,sterm=12,lterm=26,signal=9):
    macdList = []
    sigList = []
    npy = np.array(lists)
    closes = npy.T[3]
    times = npy.T[5]
    semalist = MakeEMA(closes,timelists=times,term=sterm)
    lemalist = MakeEMA(closes,timelists=times,term=lterm)
    #MACD
    for i in range(len(semalist)):
        if semalist[i] != 0 and lemalist[i] != 0:
            macdList.append(semalist[i] - lemalist[i])
        else:
            macdList.append(0)

    #シグナル
    prevdata = 0
    size = len(lists)
    for i in range(size):
        if i >= signal+1:
            bset = False
            nowtime = lists[i][5]
            prevtime = lists[i-1][5]
            if nowtime >= prevtime:
                diff = nowtime - prevtime
            else:
                diff = nowtime+60 - prevtime
            if diff != 1:
                prevdata = 0
                break
            if prevdata == 0:  #初回は単純平均を使う
                sma = MakeSMA(macdList[i-1-signal:i-1],term=signal)
                prevdata = sma[signal-1]
            if prevdata != 0:
                #当日の指数平滑平均＝前日の指数平滑平均＋α×（当日の終値-前日の指数平滑平均）
                #α＝2/(n+1)
                alpha = 2/(signal+1)
                val = prevdata+alpha*(macdList[i]-prevdata)
                sigList.append(val)
                prevdata = val
                bset = True
            if bset == False:
                sigList.append(0.)
        else:
            sigList.append(0.)
    return macdList, sigList
 
    