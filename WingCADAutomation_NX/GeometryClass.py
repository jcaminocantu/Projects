import math

class Geometry:
    def __init__(self):
        self.csysList = [] # each list index relates to section
        self.nXObjList = []
        self.sketchList = []
        self.originList = []
        self.scaleList = []
        self.numAfilePoints = 0


    # Add to List
    def addCsys(self, csys):
        temp = csys
        self.csysList.append(temp)

    def addNXObj(self, nXObject):
        temp = nXObject
        self.nXObjList.append(temp)
    
    def addSketch(self, sketch):
        temp = sketch
        self.sketchList.append(temp)

    def addOrigin(self, origin):
        temp = origin
        self.originList.append(temp)
        
    def addAfilePoint(self):
        self.numAfilePoints +=1
    
    def addScale(self, scale):
        self.scaleList.append(scale)

    
    # getters
    def getNXObj(self, indx):
        return self.nXObjList[indx]

    def getOrigin(self, indx):
        return self.originList[indx]

    def getCsys(self, indx):
        return self.csysList[indx]
        
    def getNumAfilePoints(self):
        return self.numAfilePoints

    def getSketch(self, indx):
        return self.sketchList[indx]
        
    def getScale(self, indx):
        return self.scaleList[indx]
