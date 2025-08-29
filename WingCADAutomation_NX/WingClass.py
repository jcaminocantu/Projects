#### WING OBJECT ####
from SectionClass import Section
import math
from GeometryClass import Geometry
import math
import csv
import NXOpen


class Wing:
    def __init__(self,numSects,projname):
        self.angle =0
        self.numSect = numSects
        self.sections = [] 
        self.projectName = projname
        self.dihedralAngle = 0
        self.geo = Geometry()
        

    # Parses and stores geometry data
    def readAVL(self, filename: str):
        with open(filename,'r', newline='') as file:
            reader = csv.reader(file, delimiter=" ")
            rows = list(reader)
         
            m2mm =1000# meters to mm
            
            for i in range(len(rows)):
                if len(rows[i]) == 0:
                    continue
                elif rows[i][0] == 'ANGLE':
                    self.angle = float(rows[i+1][0])
                
                elif rows[i][0] =='SECTION':
                    currRow = rows[i+2]  # row with SECTION
                    afileRow = rows[i+6]

                    newSect = Section(self.projectName)                  
                    
                    newSect.xyz = [m2mm*float(currRow[0]), m2mm*float(currRow[1]), m2mm*float(currRow[2])] 
                    newSect.chord = m2mm*float(currRow[3])  # m -> mm
                    newSect.ainc = float(currRow[4])

                    newSect.afilename = afileRow[0]
                    newSect.indx = len(self.sections)
                    newSect.afile_dat2csv()

                    self.sections.append(newSect)
       
            

    # Prints out data from all sections              
    def printSects(self):
        for i in range(self.numSect):
            print("-- Section",i,"--")
            self.sections[i].printData(self.sections[i]) 

    # Prints out Wing data + Section data
    def printWing(self):
        print("---------Printing Data---------")
        print("Angle:",self.angle)
        print("Number of Sections:",self.numSect)
        self.printSects()

    def calcDihedral(self): # in deg
        diffY = self.sections[1].getXYZ(self.sections[1])[1] - self.sections[0].getXYZ(self.sections[0])[1] # y coord is spanwise distance
        diffZ = self.sections[1].getXYZ(self.sections[1])[2] - self.sections[0].getXYZ(self.sections[0])[2] # z coord of AVL is diff height
        if (diffY == 0):
            self.dihedralAngle = 90 # vertical surface so 90 deg dihedreal
        else:
            self.dihedralAngle = math.atan(diffZ/diffY) * 180 / math.pi  

    # reads AVL and calculates dihedral
    def getData(self, filename):
        self.readAVL( filename)
        #self.calcDihedral()



    ## BUILDS ##
    def buildGeo(self):

        #inital 
        theSession  = NXOpen.Session.GetSession()
        self.theSession = theSession
        workPart = theSession.Parts.Work
        displayPart = theSession.Parts.Display
         
        markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
        theSession.SetUndoMarkName(markId1, "Datum CSYS Dialog")

        #Make Root Section 0 
        self.makeRootCsys(workPart)
        self.makeSection(workPart,theSession,0)

        #Make Rest of Sections #
        for i in range(1, self.numSect): # starts at root-adjacent section
            self.makeOffsetCsys(workPart, i) ## WRONG NEED DIFFERNET TYPE OF CSYS LOOK AT DIHEDREAL 
            self.makeSection(workPart, theSession, i)

        #Add Dihedral 
        #self.makeDihedral(workPart, theSession)

        #Make Through Curve
        self.makeThroughCurve(workPart,theSession)
    
    # makes Coordinate System
    def makeRootCsys(self,workPart):
        #postive ainc coresponds to clockwise pitch up rotation
        # ainc is surfance angle + section angle

        currSect = self.getSect(0)
      
        origin = NXOpen.Point3d(currSect.getXYZ()[0],currSect.getXYZ()[1],currSect.getXYZ()[2])
        
        self.addOrigin(origin)
        
        rootAngleTotal = self.getAngle() + currSect.getAinc()
        ainc = -rootAngleTotal * math.pi /180

        datumCsysBuilder1 = workPart.Features.CreateDatumCsysBuilder(NXOpen.Features.Feature.Null)
        xDirection1 = NXOpen.Vector3d(math.cos(ainc), 0.0, math.sin(ainc))
        yDirection1 = NXOpen.Vector3d(0.0,1.0,0.0) # hard code is fine
        xform1 = workPart.Xforms.CreateXform(origin, xDirection1, yDirection1, NXOpen.SmartObject.UpdateOption.WithinModeling, 1.0)
    
        csys = workPart.CoordinateSystems.CreateCoordinateSystem(xform1, NXOpen.SmartObject.UpdateOption.WithinModeling)
        datumCsysBuilder1.Csys = csys
        datumCsysBuilder1.DisplayScaleFactor = 1.25
        nXObject1 = datumCsysBuilder1.Commit()

        self.addCsys(csys)
        #self.addNXObj(nXObject1)   

        datumCsysBuilder1.Destroy()


    # Creates and Activiates Sketch
    def makeSketch(self,workPart, sectIndx):
        normal1 = NXOpen.Vector3d(0.0, 1.0, 0.0) # hardcode is fine
        plane1 = workPart.Planes.CreatePlane(self.getOrigin(sectIndx), normal1, NXOpen.SmartObject.UpdateOption.WithinModeling)
    
        simpleSketchInPlaceBuilder1 = workPart.Sketches.CreateSimpleSketchInPlaceBuilder()
        simpleSketchInPlaceBuilder1.UseWorkPartOrigin = False
    
        csysOrigin = self.getCsys(sectIndx).Origin
        elem =self.getCsys(sectIndx).Orientation.Element
        xDir = NXOpen.Vector3d(elem.Xx, elem.Xy, elem.Xz)
    
        csys_origin_point = workPart.Points.CreatePoint(csysOrigin) # Point not coordiante
        direction1 = workPart.Directions.CreateDirection(csysOrigin, xDir, NXOpen.SmartObject.UpdateOption.WithinModeling)
        xform2 = workPart.Xforms.CreateXformByPlaneXDirPoint(plane1, direction1, csys_origin_point, NXOpen.SmartObject.UpdateOption.WithinModeling, 0.625, False, True)
    
        csys_sketch = workPart.CoordinateSystems.CreateCoordinateSystem(xform2 ,NXOpen.SmartObject.UpdateOption.WithinModeling)
        simpleSketchInPlaceBuilder1.CoordinateSystem = csys_sketch
        simpleSketchInPlaceBuilder1.HorizontalReference.Value = direction1
    
        nXObject2 = simpleSketchInPlaceBuilder1.Commit()
        #self.addNXObj(nXObject2)
    
        sketch1 = nXObject2
        self.addSketch(sketch1)

        simpleSketchInPlaceBuilder1.Destroy()
        plane1.DestroyPlane()
        sketch1.Activate(NXOpen.Sketch.ViewReorient.TrueValue)



    def plotAfile(self, workPart, theSession, sectIndx):

        currCsys = self.getCsys(sectIndx)
        currSect = self.sections[sectIndx]
        afilenameCSV = currSect.getAfilenameCSV() # .txt csv file

        sketchSplineBuilder1 = workPart.Features.CreateSketchSplineBuilder(NXOpen.Spline.Null)
    
        origin1 = currCsys.Origin
        normal1 = NXOpen.Vector3d(0.0, 1.0, 0.0)
        plane1 = workPart.Planes.CreatePlane(origin1, normal1, NXOpen.SmartObject.UpdateOption.WithinModeling)
        sketchSplineBuilder1.DrawingPlane = plane1
        sketchSplineBuilder1.MovementPlane = plane1

        sketchSplineBuilder1.OrientExpress.ReferenceOption = NXOpen.GeometricUtilities.OrientXpressBuilder.Reference.WcsDisplayPart
        sketchSplineBuilder1.MovementMethod = NXOpen.Features.StudioSplineBuilderEx.MovementMethodType.WCS
        sketchSplineBuilder1.WCSOption = NXOpen.Features.StudioSplineBuilderEx.WCSOptionType.Y
        sketchSplineBuilder1.Degree = 2
        sketchSplineBuilder1.InputCurveOption = NXOpen.Features.StudioSplineBuilderEx.InputCurveOptions.Hide
        sketchSplineBuilder1.OrientExpress.PlaneOption = NXOpen.GeometricUtilities.OrientXpressBuilder.Plane.Passive

        sketchSplineBuilder1.IsAssociative = False
        sketchSplineBuilder1.Degree = 2

        with open(afilenameCSV, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            numRows = 0
            rows = list(reader)

            # creates Spline
            for row in rows: #for each row, take xyz and add new point to workpart

                pt = self.csys2abs_pt(workPart, currCsys, row['X'], row['Y'], row['Z'])
                geometricConstraintData1 = sketchSplineBuilder1.ConstraintManager.CreateGeometricConstraintData()
                geometricConstraintData1.Point = pt
                sketchSplineBuilder1.ConstraintManager.Append(geometricConstraintData1)


            nXObject1 = sketchSplineBuilder1.Commit()
            theSession.ActiveSketch.Update()
            sketchSplineBuilder1.Destroy()
            
             ##Adds Vertical Line
            ptStartCoords = self.csys2abs_coords(currCsys, rows[0]['X'],rows[0]['Y'],rows[0]['Z']  )
            ptEndCoords = self.csys2abs_coords(currCsys, rows[-1]['X'],rows[-1]['Y'],rows[-1]['Z'])
            line1 = workPart.Curves.CreateLine(ptStartCoords, ptEndCoords)
    
            theSession.ActiveSketch.AddGeometry(line1, NXOpen.Sketch.InferConstraintsOption.InferNoConstraints)
            theSession.ActiveSketch.Update()

       
    def makeThroughCurve(self,workPart,theSession):

        bodyType1 = theSession.Preferences.Modeling.BodyType
        throughCurvesBuilder1 = workPart.Features.CreateThroughCurvesBuilder(NXOpen.Features.Feature.Null)
        throughCurvesBuilder1.PreserveShape = False
        throughCurvesBuilder1.Alignment.AlignCurve.DistanceTolerance = 0.01
    
        throughCurvesBuilder1.Alignment.AlignCurve.ChainingTolerance = 0.0094999999999999998
        throughCurvesBuilder1.SectionTemplateString.DistanceTolerance = 0.01
        throughCurvesBuilder1.SectionTemplateString.ChainingTolerance = 0.0094999999999999998     
        throughCurvesBuilder1.Alignment.AlignCurve.AngleTolerance = 0.5
        throughCurvesBuilder1.SectionTemplateString.AngleTolerance = 0.5       


        for indx in range (0, self.numSect):
            section1 = workPart.Sections.CreateSection(0.0094999999999999998, 0.01, 0.5)  
            throughCurvesBuilder1.SectionsList.Append(section1)
            section1.SetAllowedEntityTypes(NXOpen.Section.AllowTypes.CurvesAndPoints)

            #rules
            selectionIntentRuleOptions1 = workPart.ScRuleFactory.CreateRuleOptions()
            selectionIntentRuleOptions1.SetSelectedFromInactive(False)
            features1 = [NXOpen.Features.Feature.Null] * 1 
            sketchFeature1 = self.getSketch(indx).Feature
            features1[0] = sketchFeature1
            curveFeatureRule1 = workPart.ScRuleFactory.CreateRuleCurveFeature(features1, NXOpen.DisplayableObject.Null, selectionIntentRuleOptions1)
    
            selectionIntentRuleOptions1.Dispose()
            section1.AllowSelfIntersection(False)
            section1.AllowDegenerateCurves(False)
    
            rules1 = [None] * 1 
            rules1[0] = curveFeatureRule1
            helpPoint1 = NXOpen.Point3d(0.0, 0.0, 0.0)
            section1.AddToSection(rules1, NXOpen.NXObject.Null, NXOpen.NXObject.Null, NXOpen.NXObject.Null, helpPoint1, NXOpen.Section.Mode.Create, False)
                        
            sections1 = [NXOpen.Section.Null] * 1 
            sections1[0] = section1
            throughCurvesBuilder1.Alignment.SetSections(sections1)
        
        #Finishing
        feature1 = throughCurvesBuilder1.CommitFeature()
    

        

    
    def closeSketch(self, workPart, theSession):
        sketchWorkRegionBuilder1 = workPart.Sketches.CreateWorkRegionBuilder()   
        sketchWorkRegionBuilder1.Scope = NXOpen.SketchWorkRegionBuilder.ScopeType.EntireSketch
        nXObject7 = sketchWorkRegionBuilder1.Commit()
        sketchWorkRegionBuilder1.Destroy()
        theSession.ActiveSketch.CalculateStatus()
        theSession.ActiveSketch.Deactivate(NXOpen.Sketch.ViewReorient.TrueValue, NXOpen.Sketch.UpdateLevel.Model)

        


    def makeOffsetCsys(self,workPart, sectIndx):

        #ainc is surface angle + section angle, is >0, deg

        rootCsys = self.getCsys(0)
        currSect = self.getSect(sectIndx)
        angleTotal = self.getAngle() + currSect.getAinc()
        ainc = -angleTotal # need it to be <0 This Does have to be in degrees
        
        datumCsysBuilder2 = workPart.Features.CreateDatumCsysBuilder(NXOpen.Features.Feature.Null)
        
        unit1 =workPart.UnitCollection.FindObject("Millimeter")
        unit2 = workPart.UnitCollection.FindObject("Degrees")
        
        # angles
        expression1 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit2)
        expression2 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit2)
        expression3 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit2)
        
        expression1.SetFormula("0")
        expression2.SetFormula("-"+str(ainc)+"") # change this one
        expression3.SetFormula("0.0")
        
        angleX1 = workPart.Scalars.CreateScalarExpression(expression1, NXOpen.Scalar.DimensionalityType.Angle, NXOpen.SmartObject.UpdateOption.WithinModeling) 
        angleY1 = workPart.Scalars.CreateScalarExpression(expression2, NXOpen.Scalar.DimensionalityType.Angle, NXOpen.SmartObject.UpdateOption.WithinModeling) 
        angleZ1 = workPart.Scalars.CreateScalarExpression(expression3, NXOpen.Scalar.DimensionalityType.Angle, NXOpen.SmartObject.UpdateOption.WithinModeling) 
        
        #offsets
        expression4 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit1)
        expression5 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit1)
        expression6 = workPart.Expressions.CreateSystemExpressionWithUnits("0", unit1)
        
        expression4.SetFormula(""+str(currSect.getXYZ()[0])+"")
        expression5.SetFormula(""+str(currSect.getXYZ()[1])+"") # change all three 
        expression6.SetFormula(""+str(currSect.getXYZ()[2])+"")
        
        lengthX1 = workPart.Scalars.CreateScalarExpression(expression4, NXOpen.Scalar.DimensionalityType.Length, NXOpen.SmartObject.UpdateOption.WithinModeling)
        lengthY1 = workPart.Scalars.CreateScalarExpression(expression5, NXOpen.Scalar.DimensionalityType.Length, NXOpen.SmartObject.UpdateOption.WithinModeling)    
        lengthZ1 = workPart.Scalars.CreateScalarExpression(expression6, NXOpen.Scalar.DimensionalityType.Length, NXOpen.SmartObject.UpdateOption.WithinModeling)
        
        offset1 = workPart.Offsets.CreateOffsetRectangular(lengthX1, lengthY1, lengthZ1, NXOpen.SmartObject.UpdateOption.WithinModeling)
        
        xform3 = workPart.Xforms.CreateXform(rootCsys, NXOpen.Offset.Null, offset1, angleX1, angleY1, angleZ1, 0 ,NXOpen.SmartObject.UpdateOption.WithinModeling, 1.0 )
        newSectCsys = workPart.CoordinateSystems.CreateCoordinateSystem(xform3,  NXOpen.SmartObject.UpdateOption.WithinModeling)

        datumCsysBuilder2.Csys = newSectCsys
        datumCsysBuilder2.DisplayScaleFactor = 1.25
        nXObject2 = datumCsysBuilder2.Commit()
        self.addCsys(newSectCsys)
        self.addOrigin(newSectCsys.Origin)


        datumCsysBuilder2.Destroy()   
        
    # scales obj 
    def makeScale(self,workPart, theSession, sectIndx):
    
        scaleCurveBuilder1 = workPart.Features.CurveFeatureCollection.CreateScaleCurveBuilder(NXOpen.Features.ScaleCurve.Null)
        
        currSect = self.getSect(sectIndx)
        chordString = str(currSect.getChord()*1000)
        
        scaleCurveBuilder1.UniformScaleFactor.SetFormula(chordString)
    
        scaleCurveBuilder1.CurveSettings.CurveFitData.Tolerance = 0.01
        scaleCurveBuilder1.CurveSettings.CurveFitData.AngleTolerance = 0.5
        scaleCurveBuilder1.CurveSettings.InputCurvesOption.Associative = True
        scaleCurveBuilder1.ObjectsToScale.DistanceTolerance = 0.01
        scaleCurveBuilder1.ObjectsToScale.ChainingTolerance = 0.0094999999999999998
         
        scaleCurveBuilder1.ObjectsToScale.SetAllowedEntityTypes(NXOpen.Section.AllowTypes.CurvesAndPoints)
        scaleCurveBuilder1.CurveSettings.InputCurvesOption.InputCurveOption = NXOpen.GeometricUtilities.CurveOptions.InputCurve.Retain
        
        # reference point
        datumCsys1 = self.getCsys(sectIndx)
        point1_coords = datumCsys1.Origin
        point1 =  workPart.Points.CreatePoint(point1_coords)
        point2 = workPart.Points.CreatePoint(point1, NXOpen.Xform.Null, NXOpen.SmartObject.UpdateOption.WithinModeling)
        scaleCurveBuilder1.ReferencePoint = point2
        
        #rules and objects to scale
        selectionIntentRuleOptions1 = workPart.ScRuleFactory.CreateRuleOptions()
        selectionIntentRuleOptions1.SetSelectedFromInactive(False)
    
        features1 = [NXOpen.Features.Feature.Null] * 1 
        sketchFeature1 = self.getSketch(sectIndx).Feature
        features1[0] = sketchFeature1
        curveFeatureRule1 = workPart.ScRuleFactory.CreateRuleCurveFeature(features1, NXOpen.DisplayableObject.Null)

    
        selectionIntentRuleOptions1.Dispose()
        scaleCurveBuilder1.ObjectsToScale.AllowSelfIntersection(True)
        scaleCurveBuilder1.ObjectsToScale.AllowDegenerateCurves(False)
        rules1 = [None] * 1 
        rules1[0] = curveFeatureRule1
        helpPoint1 = NXOpen.Point3d(90.958455366319043, 0.0, 258.97172092584742) # unsure what this is
        scaleCurveBuilder1.ObjectsToScale.AddToSection(rules1, NXOpen.NXObject.Null, NXOpen.NXObject.Null, NXOpen.NXObject.Null, helpPoint1, NXOpen.Section.Mode.Create, False)
        
        #finishing
        nXObject1 = scaleCurveBuilder1.Commit()
        self.addScale(nXObject1)
        
        
        scaleCurveBuilder1.ObjectsToScale.CleanMappingData()
        scaleCurveBuilder1.ObjectsToScale.CleanMappingData()
        expression2 = scaleCurveBuilder1.UniformScaleFactor
        scaleCurveBuilder1.Destroy()
        workPart.MeasureManager.SetPartTransientModification()
        workPart.MeasureManager.ClearPartTransientModification()

    # makes sketch, plots airfoil, closes sketch
    def makeSection(self,workPart,theSession, sectIndx):
        self.makeSketch(workPart, sectIndx)
        self.plotAfile(workPart, theSession,sectIndx)
        self.closeSketch(workPart, theSession)
        # self.makeScale(workPart, theSession, sectIndx)

    
    def makeDihedral(self,workPart,theSession):
        #datumCsys3 = self.getNXObj(0) # root csys Onject
        datumCsys3 = self.getCsys()
        datumCsysBuilder3 = workPart.Features.CreateDatumCsysBuilder(datumCsys3) # nXObject1 is csys1
        angleTotal = self.getAngle() + self.getSect(0).getAinc()
        ainc = angleTotal * math.pi/180 # MIGHT HAVE TO BE POSITIVE
    
        origin4 = self.getOrigin(0) # root origin
        dihedralAngle = self.getDihedral()

        xDirection2 = xDirection1 = NXOpen.Vector3d(math.cos(ainc), 0.0, math.sin(ainc)) # new vectors with dihedral rotation
        yDirection2 = NXOpen.Vector3d(math.sin(dihedralAngle) * math.sin(ainc), math.cos(dihedralAngle), -math.sin(dihedralAngle)*math.cos(ainc)) 
        xform4 = workPart.Xforms.CreateXform(origin4, xDirection2, yDirection2, NXOpen.SmartObject.UpdateOption.WithinModeling, 1.0)
    
        newRootCsys = workPart.CoordinateSystems.CreateCoordinateSystem(xform4, NXOpen.SmartObject.UpdateOption.WithinModeling)
    
        datumCsysBuilder3.Csys = newRootCsys
        datumCsysBuilder3.DisplayScaleFactor = 1.25
        nXObject3 = datumCsysBuilder3.Commit()
        datumCsysBuilder3.Destroy()
    
        # this is a work around to update the view 
        markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Dihedral")
        theSession.UpdateManager.DoUpdate(markId2)
        theSession.DeleteUndoMark(markId2,None)
        

        
    ## Getters ##
    def getAngle(self):
        return self.angle
    
    def getNumSect(self):
        return self.numSect
    
    def getSect(self, indx):
        return self.sections[indx]
    
    def getNXObj(self, indx):
        return self.geo.getNXObj(indx)
    
    def getOrigin(self, indx):
        return self.geo.getOrigin(indx)
    
    def getCsys(self,indx):
        return self.geo.getCsys(indx)
    
    def getAfilenameCSV(self,indx):
        return self.sections[indx].getAfilenameCSV()
        
    def getSketch(self, indx):
        return self.geo.getSketch(indx)
    
    def getDihedral(self):
        return self.dihedralAngle
        
    def getNumAfilePoints(self):
        return self.geo.getNumAfilePoints()
        
    def getScale(self, indx):
        return self.geo.getScale(indx)

    
    ## Adders ##
    def addCsys(self, csys):
        self.geo.addCsys(csys)

    def addNXObj(self, nxObj):
        self.geo.addNXObj(nxObj)

    def addSketch(self, sketch):
        self.geo.addSketch(sketch)
    
    def addOrigin(self, origin):
        self.geo.addOrigin( origin)
        
    def addAfilePoint(self):
        self.geo.addAfilePoint()
        
    def addScale(self, scale):
        self.geo.addScale(scale)
        
  
    
    #helpers

    # creates a point in workpart
    def csys2abs_pt(self, workPart, coordinateSystem, x,y,z):
        csysOrigin = coordinateSystem.Origin
        csysMatrix = coordinateSystem.Orientation.Element
        x= float(x)
        y = float(y)
        z = float(z)
        
     
        xo = csysOrigin.X + x * csysMatrix.Xx + y *  csysMatrix.Yx + z * csysMatrix.Zx
        yo = csysOrigin.Y
        zo = csysOrigin.Z + y *  csysMatrix.Yy

        ptcoords = NXOpen.Point3d(xo,yo,zo)
        
        pt = workPart.Points.CreatePoint(ptcoords)
        return pt
    
    # makes coords
    def csys2abs_coords(self,coordinateSystem, x,y,z):
        csysOrigin = coordinateSystem.Origin
        csysMatrix = coordinateSystem.Orientation.Element
        x= float(x)
        y = float(y)
        z = float(z)

        xo = csysOrigin.X + x * csysMatrix.Xx + y *  csysMatrix.Yx + z * csysMatrix.Zx
        yo = csysOrigin.Y
        zo = csysOrigin.Z + y *  csysMatrix.Yy

        ptcoords = NXOpen.Point3d(xo,yo,zo)        
        return ptcoords
         
        


        

    
