#-*- coding:utf-8 -*-

import os
import random
import Adf2Data as a2d
import MakeLearningData as mld

# Const
TRAIN_SIZE = 100
TEST_SIZE = 30
CNT_PER_ONEDATA = 100
NEED_FUTURE_POS = 100
train_current = 0
train_idx_list = []
test_idx_list = []
data_list = {}

#idxファイルを読み込む
def LoadIdxFile( pairName ):
    print("load idx file")
    global train_current
    global train_idx_list
    global test_idx_list

    train_current = 0
    path = '.'+os.sep+'Data'+os.sep + pairName + ".idx"
    if os.path.exists( path ) == False:
        mld.MakeData( pairName, CNT_PER_ONEDATA, NEED_FUTURE_POS )

    idxList = []
    if os.path.exists( path ) != False:
        with open( path ) as f:
            lines = f.readlines()
            for line in lines:
                idxList.append(int(line.split("\n")[0]))
        
        if len(idxList) > 0:
            size = len(idxList)
            train_list_size = int(size*(0.7))
            test_list_size = size - train_list_size
            print("train_list_size:" + str(train_list_size))
            print("test_list_size:" + str(test_list_size))
            
            train_idx_list = idxList[:train_list_size]
            test_idx_list = idxList[train_list_size+1:]

            print(str(len(train_idx_list)) + " " + str(len(test_idx_list)))
            random.shuffle(train_idx_list)
            random.shuffle(test_idx_list)
            print("load idx file success")
            return True
    return False  

#datファイルの1行を分解する
def ParseDatLineData( line ):
    d,p = mld.Data2List(line)
    return d,p

def LoadDataFile( pairName ):
    global data_list
    print("load dat file")
    counter = 0
    aryIdx = 0
    needList = train_idx_list
    needList.extend(test_idx_list)
    needList.sort()
    print( "needlistsize:"+str(len(needList)))
    path = '.'+os.sep+'Data'+os.sep + pairName + ".dat"
    print(data_list)
    if os.path.exists(path) != False:
        prev_counter = 0
        for i in needList:
            print( "needidx:"+str(i))
            counter = 0
            start = i
            end = start + CNT_PER_ONEDATA - 1
            label = end + NEED_FUTURE_POS 
            with open(path) as f:
                for line in f:
                    if prev_counter < counter:
                        if start <= counter and counter <= end:
                            d,p = ParseDatLineData(line)
                            data_list[counter] = [d,p]
                            print("add data_list:"+str(counter))
                            #print(data_list[counter])
                            prev_counter = counter
                        if counter == label:
                            d,p = ParseDatLineData(line)
                            print("add data_list:"+str(counter))
                            data_list[counter] = [d,p]
                            break
                    counter = counter+1
        if len(data_list) > 0:
            print("load dat file success")
        return len(data_list)
    return 0



def SetIdxCountSize( trainsize, testsize ):
    global train_idx_list
    global test_idx_list
    if len(train_idx_list) >= trainsize and len(test_idx_list) >= testsize:
        train_idx_list = train_idx_list[:trainsize]
        train_idx_size = len(train_idx_list)
        test_idx_list = test_idx_list[:testsize]
        test_idx_size = len(test_idx_list)
        return True
    return False

def GetData( idx ):
    global data_list
    prices = []
    for i in range(idx,idx+CNT_PER_ONEDATA-1):
        prices.append(data_list[idx][1])

def GetLabel( idx ):
    global data_list
    prices = []
    return data_list[idx+CNT_PER_ONEDATA+NEED_FUTURE_POS-1][1]   
    
def GetNextTrainData( size ):
    global train_idx_list
    global train_current
    print( "GetNextTrainData:" + str(size) )
    retDataList = []
    retLabelList = []
    for i in range( train_current, train_current + size ):
        print("need_idx:"+str(i))
        need_idx = train_idx_list[i]
        data = GetData(need_idx)
        need_idx = train_idx_list[i]
        label = GetLabel(need_idx)
        retDataList.append(data)
        retLabelList.append(label)
    train_current = train_current + size
    return retDataList,retLabelList

def GetTestData():
    print( "GetTestData"  )
    retDataList = []
    retLabelList = []
    for i in test_idx_list: 
        data = GetData(i)
        label = GetLabel(i)
        retDataList.append(data)
        retLabelList.append(label)
    return retDataList,retLabelList

#訓練用とテスト用のデータidxファイルを読み込む
if LoadIdxFile("USDJPY") != False:
    SetIdxCountSize( TRAIN_SIZE, TEST_SIZE )
    LoadDataFile("USDJPY")
    train_data,train_label = GetNextTrainData( 100 )
    test_data,test_label = GetTestData()
else:
    print("Load idx file error")
