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
NEED_FUTURE_POS = 30
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
            
            #テストと正解を分ける前にデータを分ける
            random.shuffle(idxList)
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
    d,st,hi,lo,en,cnt = mld.TickData2List(line)
    return d,float(st),float(hi),float(lo),float(en),int(cnt)


def LoadDataFile( pairName, tick, sizeofset, labelpos ):
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

    #print(data_list)

    if os.path.exists(path) != False:
        prev_counter = -1
        for i in needList:
            #print( "needidx:"+str(i))
            counter = 0
            start = i
            end = start + sizeofset
            label = end +  labelpos
            with open(path) as f:
                for line in f:
                    if prev_counter < counter:
                        if start <= counter <= label:
                            d,st,hi,lo,en,cnt = ParseTickDatLine(line)
                            data_list[counter] = [d,[st,hi,lo,en,cnt]]
                            #print("add data_list:"+str(counter))
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

def read_data_sets( pair, train_size, test_size, one_hot=False, tick=1, sizeofset=60, labelpos = 30):
    Mgr = FxDataManager(pair='USDJPY', tick=tick,sizeofset=sizeofset,labelpos=labelpos,train_size=train_size,test_size=test_size,one_hot=one_hot)
    return Mgr.MakeData()

class FxDataManager():
    def __init__(self,pair,train_size,test_size,tick=1,labelpos=1,sizeofset=60,one_hot=False):
        self.pair = pair
        self.tick = tick
        self.labelpos = labelpos
        self.sizeofset = sizeofset
        self.train_size = train_size
        self.test_size = test_size
        self.one_hot = one_hot
        self.fxTFData = None
        self.tickName = ''
    
    def GetData( self, idx ):
        global data_list
        prices = []
        for i in range(idx,idx+self.sizeofset):
            data = data_list[i]
            #print(data)
            prices.append(data[1])
        return prices

    def GetLabel( self, idx ):
        global data_list
        last_data = data_list[idx+self.sizeofset][1]
        sidx = idx+self.sizeofset+1
        lprice = float(last_data[3])

        dis_data = [0 for i in range(5)]
        for i in range(sidx,sidx+self.labelpos):
            data = data_list[i][1]
            hi = float(data[1])
            lo = float(data[2])
            hidiff = hi - lprice
            lodiff = -(lprice-lo)
            if hidiff >= 0.1:
                dis_data[0] = 1
                dis_data[1] = 0
                dis_data[3] = 0
                break
            elif hidiff >= 0.05:
                dis_data[1] = 1
            if lodiff <= -0.1:
                dis_data[4] = 1
                dis_data[1] = 0
                dis_data[3] = 0
                break
            elif lodiff <= -0.05:
                dis_data[3] = 1

        if dis_data[0] == 0 and dis_data[1] == 0 and dis_data[3] == 0 and dis_data[4] == 0:
            dis_data[2] = 1

        return dis_data

    def GetNextTrainData( self, size ):
        global train_idx_list
        global train_current
        print( "GetNextTrainData:" + str(size) )
        retDataList = []
        retLabelList = []
        for i in range( train_current, train_current + size ):
            #print("need_dx:"+str(i))
            need_idx = train_idx_list[i]
            data = self.GetData(need_idx)
            need_idx = train_idx_list[i]
            label = self.GetLabel(need_idx)
            #print('idx:{0}'.format(need_idx), label)
            retDataList.append(data)
            retLabelList.append(label)
        train_current = train_current + size
        return retDataList,retLabelList

    def GetTestData(self):
        print( "GetTestData"  )
        retDataList = []
        retLabelList = []
        for i in test_idx_list: 
            data = self.GetData(i)
            label = self.GetLabel(i)
            retDataList.append(data)
            retLabelList.append(label)
        return retDataList,retLabelList

    def getTickName(self):
        if not self.tickName:
            if self.tick == 1:
                self.tickName = "1M"
        return self.tickName
    
    def MakeTrainCachePath(self):
        # ./Data/USDJPY_data_1M_60_30.npy
        trainpath = '.'+os.sep+'Data'+os.sep + self.pair + '_data_' + self.getTickName() \
        +  '_' + str(self.sizeofset) + '_' + str(self.labelpos) + ".npy"
        # ./Data/USDJPY_label_1M_60_30.npy
        labelpath = '.'+os.sep+'Data'+os.sep + self.pair + '_label_' + self.getTickName() \
        +  '_' + str(self.sizeofset) + '_' + str(self.labelpos) + ".npy"

        return trainpath, labelpath

    #訓練・テストに利用可能なtick配列とラベルのnumpy配列を作成しSaveする
    def MakeTrainData(self):
        idxpath = '.'+os.sep+'Data'+os.sep + self.pair + self.getTickName() + ".idx"
        if os.path.exists( idxpath ) == False: 
            mld.MakeData( self.pair, self.sizeofset, self.labelpos, self.tick )

        idxList = []
        if os.path.exists( idxpath ) != False:
            with open( idxpath ) as f:
                lines = f.readlines()
                for line in lines:
                    idxList.append(int(line.split("\n")[0]))
            
            datpath = '.'+os.sep+'Data'+os.sep + self.pair + '_' + self.getTickName() + ".dat"

            if os.path.exists(datpath) != False:
                alldatList = []
                #一度全部のデータを読み込む
                with open(datpath) as f:
                    for line in f:
                        d,st,hi,lo,en,cnt = ParseTickDatLine(line)
                        alldatList.append([st,hi,lo,en,cnt])

                #データ数,セット数(60),要素数(op,hi,lo,cl,cnt)のnumpy配列を作成
                train_list = np.array([])
                #データ数,ラベル情報(10up,5up,even,5down,10down)のnumpy配列を作成
                label_list = np.array([])

                for i in idxList:
                    start = i
                    end = start + self.sizeofset
                    label = end +  self.labelpos
                    #訓練データの作成
                    for j in range(start,end):
                        train_list = np.append(train_list,alldatList[j])
                train_list = train_list.reshape(-1, self.sizeofset, 5 )
                print(train_list.shape)

                for i in idxList:
                    start = i
                    end = start + self.sizeofset
                    label = end +  self.labelpos

                    #正解データの作成
                    label_data = [0 for j in range(5)]
                    #訓練データの最後のClose値
                    lprice = alldatList[end-1][3]
                    for j in range(end,label):
                        data = alldatList[i]
                        hi = float(data[1])
                        lo = float(data[2])
                        hidiff = hi - lprice
                        lodiff = -(lprice-lo)
                        if hidiff >= 0.1:
                            label_data[0] = 1
                            label_data[1] = 0
                            label_data[3] = 0
                            break
                        elif hidiff >= 0.05:
                            label_data[1] = 1
                        if lodiff <= -0.1:
                            label_data[4] = 1
                            label_data[1] = 0
                            label_data[3] = 0
                            break
                        elif lodiff <= -0.05:
                            label_data[3] = 1

                    if label_data[0] == 0 and label_data[1] == 0 and label_data[3] == 0 and label_data[4] == 0:
                        label_data[2] = 1
                    label_list = np.append(label_list,label_data)
                label_list = label_list.reshape(-1,5)
            
            datacache, labelcache = self.MakeTrainCachePath()
            np.save( datacache, train_list ) 
            np.save( data_path, label_list ) 
        return train_list,label_list

    def LoadTrainData(self):
        datacache, labelcache = self.MakeTrainCachePath()
        if os.path.exists( datacache ) == False or os.path.exists( labelcache ) == False:
           return self.MakeTrainData()
        data = np.load(datacache)
        label = np.load(labelcache)
        return data,label
        
    def MakeData(self):
        if ExistLastData(self.pair, self.tick, self.train_size, self.test_size) != False:
            print('exist last test data,do you use this data?[y/n]')
            ret = input('>> ')
            if ret == 'y' or ret == 'Y':
                train_data,train_label,test_data,test_label = LoadLastData(self.pair,self.tick,self.train_size,self.test_size)
                fxTrainData = FxDataSet(sizeofdata=4,sizeofset=60)
                fxTrainData.setNP( train_data, train_label )
                fxTestData = FxDataSet(sizeofdata=4,sizeofset=60)
                fxTestData.setNP( test_data, test_label )
                self.fxTFData = FxTFData(self.pair,self.tick)
                self.fxTFData.set( fxTrainData, fxTestData)
                return self.fxTFData
            else:
                DeleteLastData(self.pair,self.tick,self.train_size,self.test_size)

        if self.LoadTrainData() != False:
            train_data,train_label = self.GetNextTrainData( self.train_size )
            test_data,test_label = self.GetTestData()
            fxTrainData = FxDataSet()
            fxTrainData.set( train_data, train_label )
            fxTestData = FxDataSet()
            fxTestData.set( test_data, test_label )
            self.fxTFData = FxTFData(self.pair,self.tick)
            self.fxTFData.set( fxTrainData, fxTestData)
            if self.one_hot != False:
                self.fxTFData.convOneHot()
                #self.fxTFData.convNormalize()
                self.fxTFData.save()
                return self.fxTFData
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
        ##print('convert one hot', self.datas.shape)
        self.labels = self.labels.ravel().reshape((self.sizeofbat,-1))
        #print('convert one hot', self.labels.shape)
        self.isonehot = True
    
    def print(self):
        print(self.datas)
        print(self.labels)

    def next_batch(self,size):
        spos = self.cur_pos#*self.sizeofdata*self.sizeofset
        epos = spos + size#*self.sizeofdata*self.sizeofset
        retdatas = self.datas[spos:epos]
        retlabel = self.labels[spos:epos]
        #print(retdatas.shape)
        #print(retlabel)
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

