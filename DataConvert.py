# -*- coding:utf-8 -*-
import os
import Adf2Data as a2d
import MakeLearningData as mld
import datetime
#データファイルを各Tickデータに変換する
def DatTo1Min(pairName):
    path = r'./Data/'+ pairName + ".dat"
    if os.path.exists(path) == False:
        a2d.Adf2Data( pairName )
    tick_list = []
    startTime = None
    endTime = None
    with open(path) as f:
        lines = f.readlines()
        hi = 0
        lo = 99999
        st = 0
        en = 0
        for line in lines:
            dt,price = mld.Data2List(line)
            print(dt.strftime('%Y/%m/%d %H:%M:%S')+" "+str(price))
            continue
            #未登録状態->次の分になるまでは何もしない
            if startTime == None:
                startTime = dt + datetime.timedelta(minutes=1) - datetime.timedelta(second=dt.second) - datetime.timedelta(milliseconds-dt.milliseconds)
                endTime = startTime + datatime.timedelta(minutes=1)
            else:
                if startTime < dt < endTime:
                    if hi < price:
                        hi = price
                    if lo > price:
                        lo = price
                    if st == 0:
                        st = price
                    en = price
                elif endTime <= dt:
                    startTime = None
                    if st > 0:
                        pdata = [st,hi,lo,en]
                        tick_list.append(pdata)
                        if dt - endTime <= datatime.timedelta(minutes=1):
                            startTime = endTime
                            endTime = startTime + datatime.timedelta(minutes=1)
                            st = price
                            en = price
                            hi = price
                            lo = price
                    if startTime == None:
                            startTime = dt + datetime.timedelta(minutes=1) - datetime.timedelta(second=dt.second) - datetime.timedelta(milliseconds-dt.milliseconds)
                            endTime = startTime + datatime.timedelta(minutes=1)
                            st = 0
                            en = 0
                            hi = 0
                            lo = 9999

                    
if __name__ == '__main__':
    DatTo1Min('USDJPY')
