# -*- coding:utf-8 -*-
import os
import Adf2Data as a2d
import MakeLearningData as mld
import datetime
from datetime import timedelta
import TickInfo as ti
import copy

def dt2str( dt ):
    return dt.strftime('%Y/%m/%d %H:%M:%S.%f')

def delta2minute( delta ):
    return delta.seconds/60

def writeTickData(path, listTick):
    with open(path,'w') as f:
        for tick in listTick:
            line = tick.startTime.strftime('%Y/%m/%d,%H:%M:%S.%f')+','+str(tick.st)+','+str(tick.hi)+','+str(tick.lo)+','+str(tick.en)
            print(line)
            f.write(line)
    return

def DatTo1Min(pairName):
    listTick = DataToTcik(pairName,1)
    if len(listTick) > 0:
        path = '.'+os.sep+'Data'+os.sep+ pairName + "_1M.dat"
        writeTickData(path,listTick)
    else:
        print("error make 1minute tickData")
    return
 
def DatTo15Min(pairName):
    listTick = DataToTcik(pairName,15)
    if len(listTick) > 0:
        path = '.'+os.sep+'Data'+os.sep+ pairName + "_15M.dat"
        writeTickData(path,listTick)
    else:
        print("error make 1minute tickData")
    return
    
def DataToTcik(pairName,tick):
    #データファイルを各Tickデータに変換する
    path = '.'+os.sep+'Data'+os.sep+ pairName + ".dat"
    if os.path.exists(path) == False:
        a2d.Adf2Data( pairName )
    tick_list = []
    endTime = None
    with open(path) as f:
        lines = f.readlines()
        t = None

        for line in lines:
            dt,p = mld.Data2List(line)
            price = float(p)
            #未登録状態->次の分になるまでは何もしない
            if t == None:
                startTime = dt + datetime.timedelta(minutes=tick) - datetime.timedelta(seconds=dt.second) - datetime.timedelta(microseconds=dt.microsecond)
                endTime = startTime + datetime.timedelta(minutes=tick)
                t = ti.TickInfo(stime=startTime,et=endTime)
            else:
                if t.startTime < dt < t.endTime:
                    t.updateValue(price)
                elif t.endTime <= dt:
                    size = len(tick_list)
                    #期間内だったら情報を登録する
                    if dt - t.endTime < datetime.timedelta(minutes=tick):
                        if t.containValue() == True:
                            tick_list.append(t)
                            startTime = t.endTime
                            endTime = startTime + datetime.timedelta(minutes=tick)
                            t = ti.TickInfo(price,price,price,price,startTime,endTime)
                        #期間内だけど、一度も価格の更新が行われなかった場合
                        else:
                            if size == 0:
                                startTime = dt - datetime.timedelta(seconds=dt.second) - datetime.timedelta(microseconds=dt.microsecond)
                                endTime = startTime + datetime.timedelta(minutes=tick)
                                t = ti.TickInfo(price,price,price,price,startTime,endTime)
                            else:
                                #最後のリストデータを取得する
                                lst_data = tick_list[size-1]
                                newdata = ti.TickInfo(lst_data,lst_data.en,lst_data.en,lst_data.en,t.startTime, t.endTime )
                                tick_list.append(newdata)
                                startTime = t.endTime
                                endTime = startTime + datetime.timedelta(minutes=tick)
                                t = ti.TickInfo(price,price,price,price,startTime,endTime)
                    elif dt - t.endTime <= datetime.timedelta(minutes=5):
                        add_data = None
                        add_time = None
                        if t.containValue() == True:
                            tick_list.append(t)
                            add_data = t
                            add_time = t.endTime
                        else:
                            if size > 0:
                                add_data = tick_list[size-1]
                                add_time = t.startTime
                        if add_data != None:
                            delta = dt - add_time
                            if delta > datetime.timedelta(minutes=tick):
                                delta_m = int(delta2minute(delta))
                                for i in range(0,delta_m):
                                    add_data = ti.TickInfo(add_data.en,add_data.en,add_data.en,add_data.en,add_time+datetime.timedelta(minutes=i*tick),add_time+datetime.timedelta(minutes=tick+i*tick))
                                    tick_list.append(add_data)
                        startTime = dt - datetime.timedelta(seconds=dt.second) - datetime.timedelta(microseconds=dt.microsecond)
                        endTime = startTime + datetime.timedelta(minutes=tick)
                        t = ti.TickInfo(price,price,price,price,startTime,endTime)
                    else:
                        startTime = dt + datetime.timedelta(minutes=tick) - datetime.timedelta(seconds=dt.second) - datetime.timedelta(microseconds=dt.microsecond)
                        endTime = startTime + datetime.timedelta(minutes=tick)
                        t = ti.TickInfo(startTime,endTime)
        return tick_list
        #for i in range(0,len(tick_list)):
        #    tick_list[i].printData()
                   
if __name__ == '__main__':
    #DatTo1Min('USDJPY')
    DatTo15Min('USDJPY')
