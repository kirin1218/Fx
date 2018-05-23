# -*- coding:utf-8 -*-
import Fx
import os
import TickInfo as ti

def AnalyzeChangeDistrbution(pairName, tick, labelpos):
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


if __name__ == '__main__':
    AnalyzeChangeDistrbution( 'USDJPY', 1, 10 )
