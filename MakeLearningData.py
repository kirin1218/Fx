#-*- coding:utf-8 -*-

import os
import datetime
import Adf2Data as a2d

def Data2List( line ):
    #2016/10/18,08:26:46.123,103.865
    cells = line.split(',')

    date = cells[0].split('/')
    time = cells[1].split(':')
    seconds = time[2].split('.')
    if len(seconds) == 1:
        return None,0
    price = cells[2]

    d = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),
            int(time[0]),int(time[1]),int(seconds[0]),int(seconds[1])*1000)

    return d, price

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

def checkdata( start, cnt, listData ):
    if start + cnt + 100 >= len(listData):
        return False
    prevDate = None
    for i in range( start, start + cnt + 100 ):
        if checktime( listData[i][0] ) == False or checkprice( listData[i][1] ) == False:
               
            print(listData[i])
            return False
        if prevDate != None:
            d = prevDate + datetime.timedelta(minutes=10)
            if d < listData[i][0]:
                print(prevDate)
                print(listData[i][0])
                return False
        prevDate = listData[i][0] 

    return True

def MakeData( pairName ):
    path = ".\\Data\\"+ pairName + ".dat"
    if os.path.exists(path) == False:
        a2d.Adf2Data( pairName )
        
    priceData = []
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            d,price = Data2List(line)
            if d != None:
                priceData.append([d,float(price)])

    print("check start")
    listDataIdxs = []
    for i in range(0,len(priceData)):
        if i % 1000 == 0:
            print(i)
        if checkdata( i, 1000, priceData ) == True:
            listDataIdxs.append(i)

    if len(listDataIdxs) > 0:
        with open( ".\\Data\\" + pairName + ".idx",'w') as f:
            for idx in listDataIdxs:
                f.write(str(idx)+"\n")

