#-*- coding:utf-8 -*-

import os
import random
import Adf2Data as a2d
import MakeLearningData as mld
import DataConvert as dc
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf

# Const
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
    Mgr = FxDataManager(pair=pair, tick=tick,sizeofset=sizeofset,labelpos=labelpos,train_size=train_size,test_size=test_size,one_hot=one_hot)
    return Mgr.MakeData()

def showCandle2( nplist ):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        nary = np.zeros((60,4),dtype=float)

        fxary = nplist.reshape(60,5)
        for i in range(60):
            data = fxary[i] 
            nary[i] = [data[0],data[1],data[2],data[3]]
        
        tary = nary.T
        mpf.candlestick2_ohlc(ax,opens=tary[0],highs=tary[1],lows=tary[2],closes=tary[3],width=0.7, colorup='g', colordown='r')
        ax.grid()
        plt.show()


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
        self.alltrainlist = None
        self.alllabellist = None
    
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

        dis_data = [0 for i in range(3)]
        for i in range(sidx,sidx+self.labelpos):
            data = data_list[i][1]
            hi = float(data[1])
            lo = float(data[2])
            hidiff = hi - lprice
            lodiff = -(lprice-lo)
            if hidiff >= 0.05:
                dis_data[0] = 1
                break
            if lodiff <= -0.05:
                dis_data[2] = 1
                break

        if dis_data[0] == 0 and dis_data[2] == 0:
            dis_data[1] = 1
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

    def MakeCandleListWith1MList(self, train_list, term ):
        for i in range(len(train_list) ):
            doextend = False
            cur = train_list[i]
            m = cur[5]
            cnt = m%term
            stock = []
            if cnt == 0:
                for j in range(term):
                    add = train_list[i+j]
                    #  データが連続してなかったら抜ける
                    if add[5]%term != j:
                        break
                    if i + j < len(train_list):
                        stock.append(add)
                size = len(stock)
                if size > 0:
                    Op = stock[0][0]
                    Cl = stock[size-1][3]
                    Hi = 0
                    Lo = 999999
                    for j in range(size):
                        if Hi < stock[j][1]:
                            Hi = stock[j][1]
                        if Lo > stock[j][2]:
                            Lo = stock[j][2]
                for j in range(size):
                    train_list[i+j].extend([Op,Hi,Lo,Cl])
                    doextend = True
            if doextend == False:
                train_list[i].extend([0,0,0,0])

    #訓練・テストに利用可能なtick配列とラベルのnumpy配列を作成しSaveする
    def MakeTrainData(self):
        idxpath = '.'+os.sep+'Data'+os.sep + self.pair + '_' + self.getTickName() + ".idx"
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
                        m = d.minute
                        alldatList.append([st,hi,lo,en,cnt,m])

                #1分足から5分足のリストを作成する
                self.MakeCandleListWith1MList(alldatList,5)

                cnt1 = 0
                allcount = len(idxList)
                #データ数,セット数(60),要素数(op,hi,lo,cl,cnt)のnumpy配列を作成
                train_list = np.zeros(([allcount,self.sizeofset,6]),dtype=float)
                #データ数,ラベル情報(10up,5up,even,5down,10down)のnumpy配列を作成
                label_list = np.zeros(([allcount,3]),dtype=float)

                for i in idxList:
                    start = i
                    end = start + self.sizeofset
                    label = end +  self.labelpos
                    cnt2 = 0
                    #訓練データの作成
                    for j in range(start,end):
                        train_list[cnt1][cnt2] = alldatList[j]
                        cnt2+=1
                    if cnt1%100 == 0:
                        print('MakeTrainData(data):',cnt1,'/',allcount)

                    cnt1+=1
                #train_list = train_list.reshape(-1, self.sizeofset, 5 )
                print(train_list.shape)

                cnt1 = 0
                for i in idxList:
                    start = i
                    end = start + self.sizeofset
                    label = end +  self.labelpos

                    #正解データの作成
                    label_data = [0 for j in range(3)]
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
                            break
                        if lodiff <= -0.1:
                            label_data[2] = 1
                            break

                    if label_data[0] == 0 and label_data[2] == 0:
                        label_data[1] = 1

                    label_list[cnt1] = label_data
                    if cnt1%100 == 0:
                        print('MakeTrainData(label):',cnt1,'/',allcount)
                    cnt1+=1
                print(label_list.shape)
            
            datacache, labelcache = self.MakeTrainCachePath()
            #np.save( datacache, train_list ) 
            #np.save( labelcache, label_list ) 
        batsize = train_list.shape[0]
        batsize2 = label_list.shape[0]

        if batsize > 0 and batsize == batsize2:
            return train_list,label_list
        else:
            return None, None

    def LoadTrainData(self):
        datacache, labelcache = self.MakeTrainCachePath()
        if os.path.exists( datacache ) == False or os.path.exists( labelcache ) == False:
           return self.MakeTrainData()
        data = np.load(datacache)
        label = np.load(labelcache)
        return data,label
    
    def GetLabelDistribution(self,lists):
        labelary = np.sum(lists,axis=0)
        return labelary

    def ExtractDataByMinsize(self,dataary,labelary,minsize):
        datalistbylabel = {}
        labellistbylabel = {}

        for i in range(0,labelary.shape[0]):
            label = labelary[i]
            idxary = np.where(label==1)
            idx = idxary[0][0]
            if not (idx in datalistbylabel.keys()):
                datalistbylabel[idx] = []
                labellistbylabel[idx] = []

            #if len(datalistbylabel[idx]) < size:
            datalistbylabel[idx].append(dataary[idx])
            labellistbylabel[idx].append(label)
        retdata = []
        retlabel = [] 
        for i in range(labelary.shape[1]):
            npdata = np.array(datalistbylabel[i])
            nplabel = np.array(labellistbylabel[i])

            #print(label,idx)
            randomidx = random.sample(range(len(datalistbylabel[i])),int(minsize))
            tempdata = npdata[randomidx]
            templabel = nplabel[randomidx]
            retdata.extend(tempdata)
            retlabel.extend(templabel)
        
        randomidx = random.sample(range(len(retlabel)),len(retlabel))
        npdata = np.array(retdata)
        nplabel = np.array(retlabel)
        retdata = npdata[randomidx]
        retlabel = nplabel[randomidx]
        
        return retdata,retlabel

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

        self.alltrainlist, self.alllabellist = self.LoadTrainData() 
        #for i in range(self.alltrainlist.shape[0]):
        #    showCandle2(self.alltrainlist[i])

        if self.alltrainlist is not None and self.alllabellist is not None:
            #バッチサイズ
            max_size = self.alltrainlist.shape[0]
            print('max_size:',max_size)
            label_size = int(max_size*0.8)
            #正解用のデータを分布をきにせずに取り出す
            test_data_area = self.alltrainlist[label_size:]
            test_label_area = self.alllabellist[label_size:]
            train_data_area = self.alltrainlist[:label_size]
            train_label_area = self.alllabellist[:label_size]

            #テストデータを作成
            randomidx = random.sample(range(len(test_data_area)),self.test_size)
            test_data_cond = np.array(test_data_area) 
            test_label_cond = np.array(test_label_area) 
            test_data = test_data_cond[randomidx] 
            test_label = test_label_cond[randomidx] 
            #正解データの個数を取得
            labelDist = self.GetLabelDistribution(train_label_area)
            minElement = np.min(labelDist)
            train_data,train_label = self.ExtractDataByMinsize(train_data_area,train_label_area,minElement)

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
    
    def pos_reset(self):
        self.cur_pos = 0
        
    def save(self,pair,tick,size):
        data_path,label_path = MakeLastDataPath(pair,tick,size)
        np.save( data_path, self.datas)
        np.save( label_path, self.labels)

    def showCandle( self, idx ):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        nary = np.zeros((self.sizeofset,4),dtype=float)

        fxary = self.datas[idx].reshape((self.sizeofset,self.sizeofdata))
        fxlabelary = self.labels[idx]
        idxary = np.where(fxlabelary==1)
        idx = idxary[0][0]
        plt.title('label:' + str(idx))
        #ax.title = 'label:' + str(idx)
        for i in range(self.sizeofset):
            data = fxary[i] 
            nary[i] = [data[0],data[1],data[2],data[3]]
        
        tary = nary.T
        mpf.candlestick2_ohlc(ax,opens=tary[0],highs=tary[1],lows=tary[2],closes=tary[3],width=0.7, colorup='g', colordown='r')
            #mpf.candlestick_ohlc(ax,[op,hi,lo,cl],width=0.7, colorup='g', colordown='r')
        ax.grid()
        plt.show()


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

    #入力データ整形
    num_seq = 5
    num_input = 60
    num_weight = 128
    num_result = 3

    #mnistデータを格納しimpoたオブジェクトを呼び出す
    #mnist = input_data.read_data_sets("data/", one_hot=True)
    fxDS = read_data_sets('USDJPY', train_size=200,test_size=50,one_hot=True)
    #for i in range(200):
    #    print(fxDS.train.datas[i])
    #for i in range(199):
    #    fxDS.train.showCandle(i)
