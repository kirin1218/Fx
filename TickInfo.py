#-*- coding:utf-8 -*-

class TickInfo():
    def __init__(self,st=0.0,hi=0.0,lo=999999.0,en=0.0,stime=None,et=None):
        self.initVal()
        self.st = st
        self.hi = hi
        self.lo = lo
        self.en = en
        self.setTime(stime,et)
        if self.startTime is None or self.endTime is None:
            a = 3

    def printData(self):
        print(self.startTime,self.endTime,self.st,self.hi,self.lo,self.en)

    def containValue(self):
        if self.st != 0:
            return True
        else:
            return False

    def initVal(self):
        self.st = 0
        self.hi = 0
        self.lo = 999999
        self.en = 0
        self.startTime = None
        self.endTime = None
  
    def setTime(self,st=None,et=None):
        self.startTime = st
        self.endTime = et
    
    def updateValue(self,price):
        if self.hi < price:
            self.hi = price
        if self.lo > price:
            self.lo = price
        if self.st == 0:
            self.st = price
        self.en = price
