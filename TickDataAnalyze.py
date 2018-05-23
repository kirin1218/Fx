# -*- coding:utf-8 -*-

def AnalyzeChangeDistrbution(pairName, tick, labelpos):
    tick_name = ''
    if tick == 1:
        tick_name = '_1M'
    path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".dat"

    with open( path ) as f:
            lines = f.readlines()
            for line in lines:
                idxList.append(int(line.split("\n")[0]))
        



if __name__ == '__main__':
