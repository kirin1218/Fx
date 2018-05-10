# -*- coding:utf-8 -*-
# CONST
ADF_DIR_NAME = "ADF"
COUNT_PER_TIME = 1000
GET_PRICE_TERM = 10

import os
import glob
import datetime
def WriteMergeData( priceList, pairName ):
    with open(r'./Data/' + pairName + ".dat", 'w') as f:
        for line in priceList:
            f.writelines(line)


#�t�@�C���p�X�ƃt�@�C����1��ڏ�񂩂���t��쐬����
def makeDateTime( path, col ) -> datetime:
    #path->���t
    # ex) .\adf\usdjpy\2018\01\03.adf -> xxx,2018,01,03
    print(path)
    dirs = path.rsplit(r'/',3)
    dirs[3] = dirs[3].split(".")[0]

    #1��ڃf�[�^��Ԃɕϊ�
    #hh:mm:ss.sss -> hh,mm,ss,sss
    seconds = col.split(".")
    if len(seconds) == 1:
        seconds.append("000")
    times = seconds[0].split(":")
    times.append(seconds[1])

    d = datetime.datetime(int(dirs[1]),int(dirs[2]),int(dirs[3]),
            int(times[0]),int(times[1]),int(times[2]),int(times[3]))
    return d

def checkData(listData, curIdx, continueCnt):
    if curIdx + continueCnt >= len(listData):
        return False

    prevDate = None
    for i in range(curIdx, curIdx+continueCnt):
        d = GetDateTime(listData[i])
        
def Adf2Data( pairName ):        
    listADF = glob.glob(r'./'+ADF_DIR_NAME+r'/'+pairName+r'/**/*.adf',recursive=True)

    priceData = {}
    data = []

    for adf in listADF:
        #adf->���t
        # ex) .\adf\usdjpy\2018\01\03.adf -> xxx,2018,01,03
        print(adf)
        dirs = adf.rsplit(r'/',3)
        dirs[3] = dirs[3].split(".")[0]
        date = dirs[1] + r'/' + dirs[2] + r'/' + dirs[3]

        with open(adf) as f:
            lines = f.readlines()
            for line in lines:
                data.append(date + "," + line)

    WriteMergeData(data,pairName)
