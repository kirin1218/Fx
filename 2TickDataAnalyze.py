# -*- coding:utf-8 -*-
import Fx
import os
import TickInfo as ti
import datetime as dt
import matplotlib.pyplot as plt
import mataplotlib.finance as mpf

def AnalyzeChangeDistrbution(pairName, tick, sizeofset, labelpos):
    if Fx.LoadIdxFile(pairName, tick) != False:
        tick_name = ''
        if tick == 1:
            tick_name = '_1M'
        path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".dat"
        ticklist = []
        with open( path ) as f:
            lines = f.readlines()
            for line in lines:
                d,st,hi,lo,en,cnt = Fx.ParseTickDatLine(line)
                ticklist.append(ti.TickInfo(st,hi,lo,en,stime=d,cnt=cnt))

        for i in range(0,len(ticklist)):
            if i + sizeofset -1 + labelpos >= len(ticklist):
                break
            starttick = ticklist[i]
            endtick = ticklist[i+sizeofset-1]
            futuretick = ticklist[i+sizeofset-1+labelpos]
            checktime = starttick.startTime + dt.timedelta(minutes=labelpos+sizeofset-1)
            if futuretick.startTime == checktime:
                #diff = [] 
                tu10 = tu5 = td5 = td10 = 0
                for j in range(labelpos):
                    hidiff = ticklist[i+sizeofset+j].hi-endtick.en
                    lodiff = endtick.en - ticklist[i+sizeofset+j].lo
                    if hidiff >= 0.1:
                        tu10 = 1
                    elif hidiff > 0.05:
                        tu5 = 1
                    
                    if lodiff <= -0.1:
                        td10 = 1
                    elif lodiff <= -0.05:
                        td5 = 1

                starttick.setFutureData([tu10,tu5,td5,td10])
        for i in range(0,len(ticklist)):
            data = ticklist[i].futuredata
            if data is not None and len(data) == 4:
                if data[0] == 1 and data[1] == 1 and data[2] == 1 and data[3] == 1:
                    showCandle(ticklist[i])


def showCandle( listdata ):
    fig = plt.figure()
    ax = plt.subplot()

    for data in listdata:
        mpf.candlestick2_ohlc(ax,data.st,data.hi,data.lo,data.en,width=0.7, colorup='g', colordown='r')
    ax.grid()
    fig.show()

if __name__ == '__main__':
    AnalyzeChangeDistrbution( 'USDJPY', 1, 60, 30 )

