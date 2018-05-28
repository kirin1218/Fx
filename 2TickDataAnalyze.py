# -*- coding:utf-8 -*-
import Fx
import os
import TickInfo as ti
import datetime as dt
import matplotlib.pyplot as plt
import mpl_finance as mpf
import numpy as np

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
                    lodiff = -(endtick.en - ticklist[i+sizeofset+j].lo)
                    if hidiff >= 0.1:
                        tu10 = 1
                    elif hidiff > 0.05:
                        tu5 = 1
                    
                    if lodiff <= -0.1:
                        td10 = 1
                    elif lodiff <= -0.05:
                        td5 = 1

                starttick.setFutureData([tu10,tu5,td5,td10])
        up10 = up = dn = dn10 =  eq = 0
        for i in range(0,len(ticklist)):
            data = ticklist[i].futuredata
            if data is not None and len(data) == 4:
                if data[0] == 1:
                    up10 += 1
                elif data[1] == 1:
                    #showCandle(ticklist,i,labelpos)
                    up+=1
                elif data[3] == 1:
                    dn10+=1
                elif data[2] == 1:       
                    #showCandle(ticklist,i,labelpos)
                    dn+=1
                else:
                    eq+=1
        print( 'up 10tips:{0}:{3} down 10tips:{1}:{4} all:{2}'.format(up, dn, up+dn+eq+up10+dn10, up10, dn10))


def showCandle( lists, idx, labelpos ):
    fig = plt.figure()
    #ax = plt.subplot(1,1,1)
    ax = fig.add_subplot(1,1,1)
    nary = np.zeros((labelpos,4),dtype=float)

    for i in range(idx,idx+labelpos):
        data = lists[i]
        nary[i-idx] = [data.st,data.hi,data.lo,data.en]
    
    tary = nary.T
    mpf.candlestick2_ohlc(ax,opens=tary[0],highs=tary[1],lows=tary[2],closes=tary[3],width=0.7, colorup='g', colordown='r')
        #mpf.candlestick_ohlc(ax,[op,hi,lo,cl],width=0.7, colorup='g', colordown='r')
    ax.grid()
    plt.show()

if __name__ == '__main__':
    AnalyzeChangeDistrbution( 'USDJPY', 1, 60, 10 )

