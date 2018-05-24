# -*- coding:utf-8 -*-
import Fx
import os
import TickInfo as ti
import datetime as dt
import matplotlib.pyplot as plt

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
                diff = [] 
                for j in range(labelpos):
                    diff.append(ticklist[i+sizeofset+j].en-endtick.en)
                starttick.setFutureData(diff)
        
        Ana = []
        for j in range(labelpos):
            adddata = {}
            for i in range(0,len(ticklist)):
                if len(ticklist[i].futuredata) == labelpos:
                    val = round(ticklist[i].futuredata[j],5)
                    if val in adddata:
                        adddata[val] = adddata[val] + 1
                    else:
                        adddata[val] = 1
            adddata = sorted(adddata.items())
            Ana.append(dict(adddata))
        print(type(Ana))
        plt.plot(Ana[0].keys(),Ana[0].values())
        plt.show()

            
 


if __name__ == '__main__':
    AnalyzeChangeDistrbution( 'USDJPY', 1, 60, 10 )
