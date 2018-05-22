#-*- coding:utf-8 -*-

import os
import random
import Adf2Data as a2d
import MakeLearningData as mld
import DataConvert as dc
import numpy as np

# Const
TRAIN_SIZE = 100
TEST_SIZE = 30
CNT_PER_ONEDATA = 60
NEED_FUTURE_POS = 1
train_current = 0
train_idx_list = []
test_idx_list = []
data_list = {}

#idxファイルを読み込む
def LoadIdxFile( pairName, tick ):
    print("load idx file")
    global train_current
    global train_idx_list
    global test_idx_list

    tick_name = ''
    if tick == 1:
        tick_name = '_1M'
    train_current = 0
    path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".idx"

    if os.path.exists( path ) == False:
        mld.MakeData( pairName, CNT_PER_ONEDATA, NEED_FUTURE_POS, tick )

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

def ParseTickDatLine( line ):
    d,st,hi,lo,en = mld.TickData2List(line)
    return d,st,hi,lo,en


def LoadDataFile( pairName, tick ):
    global data_list
    print("load dat file")
    counter = 0
    needList = train_idx_list
    needList.extend(test_idx_list)
    needList.sort()
    print( "needlistsize:"+str(len(needList)))

    tick_name = ''
    if tick == 1:
        tick_name = '_1M'
    path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + ".dat"

    print(data_list)

    if os.path.exists(path) != False:
        prev_counter = -1
        for i in needList:
            print( "needidx:"+str(i))
            counter = 0
            start = i
            end = start + CNT_PER_ONEDATA
            label = end + NEED_FUTURE_POS 
            with open(path) as f:
                for line in f:
                    if prev_counter < counter:
                        if ( start <= counter <= end ) or counter == label:
                            d,st,hi,lo,en = ParseTickDatLine(line)
                            data_list[counter] = [d,[st,hi,lo,en]]
                            print("add data_list:"+str(counter))
                            if counter == label:
                                break
                            prev_counter = counter
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
        test_idx_list = test_idx_list[:testsize]
        return True
    print( "error shortage data train:{0} test:{1}".format( \
        len(train_idx_list),len(test_idx_list)))
    return False

def GetData( idx ):
    global data_list
    prices = []
    for i in range(idx,idx+CNT_PER_ONEDATA):
        data = data_list[i]
        print(data)
        prices.append(data[1])
    return prices
min_diff = 99999.99
max_diff = 0.0
def GetLabel( idx ):
    global data_list
    global min_diff
    global max_diff
    last_data = data_list[idx+CNT_PER_ONEDATA][1]
    price = data_list[idx+CNT_PER_ONEDATA+NEED_FUTURE_POS][1]
    diff = float(last_data[3])-float(price[3])
    if min_diff > diff:
        min_diff = diff
    if max_diff < diff:
        max_diff = diff
    #~-3|-3~-1|-1~1|1~3|3~|
    labels = [0 for i in range(5)]
    label = 2
    if diff < -0.03:
        label = 0
    elif -0.03 <= diff <= -0.01:
        label = 1
    elif -0.01 <= diff <= 0.01:
        label = 2
    elif 0.01 < diff <= 0.03:
        label = 3
    elif 0.03 < diff:
        label = 4
    labels[label] = 1

    return labels
    
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
    global min_diff
    global max_diff
    return retDataList,retLabelList

def MakeLastDataPath(pairName,tick,size):
    tick_name = ''
    if tick == 1:
        tick_name = '_1M'
    data_path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + '_data_' + str(size) + ".npy"
    label_path = '.'+os.sep+'Data'+os.sep + pairName + tick_name + '_label_' + str(size) + ".npy"
    return data_path,label_path


def ExistLastData(pairName,tick,train_size,test_size):
    traind_path,trainl_path = MakeLastDataPath(pairName,tick,train_size)
    testd_path,testl_path = MakeLastDataPath(pairName,tick,test_size)
    if os.path.exists(traind_path) == False or  os.path.exists(trainl_path) == False or os.path.exists(testd_path) == False or os.path.exists(testl_path) == False:
        return False
    else:
        return True

def DeleteLastData(pairName,tick,train_size,test_size):
    traind_path,trainl_path = MakeLastDataPath(pairName,tick,train_size)
    testd_path,testl_path = MakeLastDataPath(pairName,tick,test_size)
    os.remove(traind_path)
    os.remove(trainl_path)
    os.remove(testd_path)
    os.remove(testl_path)


def LoadLastData(pairName,tick,train_size,test_size):
    traind_path,trainl_path = MakeLastDataPath(pairName,tick,train_size)
    testd_path,testl_path = MakeLastDataPath(pairName,tick,test_size)
    traind = np.load(traind_path)
    trainl = np.load(trainl_path)
    testd = np.load(testd_path)
    testl = np.load(testl_path)
    return traind,trainl,testd,testl

def read_data_sets( train_size, test_size, one_hot=False):
    if ExistLastData("USDJPY", 1, train_size, test_size) != False:
        print('exist last test data,do you use this data?[y/n]')
        ret = input('>> ')
        if ret == 'y' or ret == 'Y':
            train_data,train_label,test_data,test_label = LoadLastData("USDJPY",1,train_size,test_size)
            fxTrainData = FxDataSet(sizeofdata=4,sizeofset=60)
            fxTrainData.setNP( train_data, train_label )
            fxTestData = FxDataSet(sizeofdata=4,sizeofset=60)
            fxTestData.setNP( test_data, test_label )
            fxTFData = FxTFData('USDJPY',1)
            fxTFData.set( fxTrainData, fxTestData)
            return fxTFData
        else:
            DeleteLastData("USDJPY",1,train_size,test_size)

    if LoadIdxFile("USDJPY", 1) != False:
        if SetIdxCountSize( train_size, test_size ) != False:
            if LoadDataFile("USDJPY",1) > 0:
                train_data,train_label = GetNextTrainData( train_size )
                test_data,test_label = GetTestData()
                fxTrainData = FxDataSet()
                fxTrainData.set( train_data, train_label )
                fxTestData = FxDataSet()
                fxTestData.set( test_data, test_label )
                fxTFData = FxTFData('USDJPY',1)
                fxTFData.set( fxTrainData, fxTestData)
                if one_hot != False:
                    fxTFData.convOneHot()
                fxTFData.convNormalize()
                fxTFData.save()
                return fxTFData
    return None

class FxDataSet():
    def __init__(self,sizeofset=1,sizeofdata=1):
        self.datas = None 
        self.labels = None
        self.sizeofdata = sizeofdata
        self.sizeofset = sizeofset
        self.sizeofbat = 1
        self.cur_pos = 0
        self.isonehot = False

    def set( self, datas, labels ):
        self.datas = np.array(datas,dtype=float)
        self.labels = np.array(labels,dtype=int)
        self.sizeofbat = self.datas.shape[0]
        self.sizeofset = self.datas.shape[1]
        self.sizeofdata = self.datas.shape[2]

    def setNP( self, datas, labels ):
        self.datas = datas
        self.labels = labels
        self.sizeofbat = self.datas.shape[0]

    def zscore( self, x, axis=None ):
        xmean = x.mean(axis=axis, keepdims=True)
        xstd = np.std(x, axis=axis, keepdims=True)
        zscore = (x-xmean)/xstd
        return zscore

    def convNormalize( self ):
        self.datas = self.zscore(self.datas)

    def convOneHot( self ):
        self.datas = self.datas.ravel().reshape((-1,self.sizeofset*self.sizeofdata))
        print('convert one hot', self.datas.shape)
        self.labels = self.labels.ravel().reshape((self.sizeofbat,-1))
        print('convert one hot', self.labels.shape)
        self.isonehot = True
    
    def print(self):
        print(self.datas)
        print(self.labels)

    def next_batch(self,size):
        spos = self.cur_pos#*self.sizeofdata*self.sizeofset
        epos = spos + size#*self.sizeofdata*self.sizeofset
        retdatas = self.datas[spos:epos]
        retlabel = self.labels[spos:epos]
        print(retdatas.shape)
        print(retlabel)
        self.cur_pos += size
        return retdatas, retlabel
    
    def save(self,pair,tick,size):
        data_path,label_path = MakeLastDataPath(pair,tick,size)
        np.save( data_path, self.datas)
        np.save( label_path, self.labels)

class FxTFData():
    def __init__(self, pair, tick):
        self.train =[]
        self.test = []
        self.train_size = 0
        self.test_size = 0
        self.tick = tick
        self.pair = pair
    
    def set( self, train, test ):
        self.train = train
        self.train_size  = train.sizeofbat
        self.test = test
        self.test_size = test.sizeofbat

    def convOneHot( self ):
        self.train.convOneHot()
        self.test.convOneHot()

    def convNormalize( self ):
        self.train.convNormalize()
        self.test.convNormalize()
    
    def save(self):
        self.train.save(self.pair,self.tick,self.train_size)
        self.test.save(self.pair,self.tick,self.test_size)
    
if __name__ == '__main__':
    train_data = [[[1.2,2.3],[3.4,5.6]],[[1.2,2.3],[3.4,5.6]]]
    train_label = [[0,1,0],[1,0,0]]
    fxTrainData = FxDataSet()
    fxTrainData.set( train_data, train_label )
    fxTrainData.convOneHot()
    fxTrainData.convNormalize()

