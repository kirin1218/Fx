#-*- coding:utf-8 -*-

import os
import datetime
import Adf2Data as a2d
import DataConvert as dc

def Data2List( line ):
    #2016/10/18,08:26:46.123,103.865
    cells = line.split(',')

    date = cells[0].split(os.sep)
    time = cells[1].split(':')
    seconds = time[2].split('.')
    if len(seconds) == 1:
        seconds.append('000')
        #return None,0
    price = cells[2].split('\n')[0]
    d = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),
            int(time[0]),int(time[1]),int(seconds[0]),int(seconds[1])*1000)

    return d, price

def TickData2List( line ):
    #2016/10/18,08:26:46.123,103.865
    cells = line.split(',')

    date = cells[0].split('/')
    time = cells[1].split(':')
    seconds = time[2].split('.')
    if len(seconds) == 1:
        seconds.append('000')
        #return None,0
    st = cells[2]
    hi = cells[3]
    lo = cells[4]
    en = cells[5]
    cnt = cells[6].split('\n')[0]
    d = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),
            int(time[0]),int(time[1]),int(seconds[0]),int(seconds[1])*1000)

    return d, st, hi, lo, en, cnt


def checktime( date ):
    if 2000 < date.year and date.year < 3000:
        if 1 <= date.month and date.month <= 12:
            if 1 <= date.day and date.day <= 31:
                if 0 <= date.hour and date.hour <= 24:
                    if 0 <= date.minute and date.minute <= 60:
                        if 0 <= date.second and date.second <= 60:
                            return True;

    return False

def checkprice( price ):
    if 50 < price and price < 300:
        return True
    return False

def checkdata( start, cnt, listData, needFuturePos, tick ):
    if start + cnt + needFuturePos >= len(listData):
        return False
    prevDate = None
    for i in range( start, start + cnt + needFuturePos ):
        if checktime( listData[i][0] ) == False \
         or checkprice( listData[i][1] ) == False \
         or checkprice( listData[i][2] ) == False \
         or checkprice( listData[i][3] ) == False \
         or checkprice( listData[i][4] ) == False:
               
            print(listData[i])
            return False
        if prevDate != None:
            d = prevDate + datetime.timedelta(minutes=tick)
            if d < listData[i][0]:
                print(prevDate)
                print(listData[i][0])
                return False
        prevDate = listData[i][0] 

    return True
import pandas as pd
def MakeData( pairName, cntPerOneData, needFuturePos, tick ):
    tick_name = ''
    if tick == 1:
        tick_name = '_1M'
    path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".dat"
    if os.path.exists(path) == False:
        datapath = '.'+os.sep+'Data'+os.sep + pairName + ".dat"
        if os.path.exists(datapath) == False:
            print("dat file not exist!")
            a2d.Adf2Data( pairName )
        if tick == 1:
            dc.DatTo1Min(pairName)
        else:
            path = datapath
    csv_path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".csv"
    if os.path.exists(csv_path) == False:
        clmn = ['Date','Open','High','Low','Close','UpdateCount']
        tick_list = pd.DataFrame(index=[],columns=clmn)
        if tick == 1:
            with open(path) as f:
                lines = f.readlines()
                for line in lines:
                    d,st,hi,lo,en,cnt = TickData2List(line)
                    if d != None:
                        if type(st) is str:
                            tinfo = pd.Series([d,float(st),float(hi),float(lo),float(en),int(cnt)],index=tick_list.columns)
                            tick_list = tick_list.append(tinfo, ignore_index = True)  
                        else:
                            print(type(st))
        if tick_list.size() > 0:
            tick_list.to_csv(csv_path)

'''
        print("check start")
        listDataIdxs = []
        for i in range(0,len(priceData)):
            if checkdata( i, cntPerOneData, priceData, needFuturePos, tick ) == True:
                listDataIdxs.append(i)

        if len(listDataIdxs) > 0:
            with open( '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".idx",'w') as f:
                for idx in listDataIdxs:
                    f.write(str(idx)+"\n")
'''
