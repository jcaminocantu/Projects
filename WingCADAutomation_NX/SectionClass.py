import csv

#####  SECTION OBJECT #####
class Section:
    def __init__(self,projName):
        self.xyz = [0.0,0.0,0.0]
        self.chord = 0.0
        self.ainc = 0.0
        self.afilename = ""
        self.afilenameCSV = ""
        self.indx = 0
        self.projectName = projName
    
    def printData(self):
        print(self.xyz )
        print(self.chord )
        print(self.ainc )
        print(self.afilename )
        print(self.afilenameCSV)



    def afile_dat2csv(self):

        writefile = self.projectName + '_sect_' + str(self.indx)+'.txt' # renames outfile
        self.afilenameCSV = writefile

        with open (self.afilename, 'r') as file:
            with open(writefile, 'w', newline='') as wrfile:
                reader = csv.reader(file, delimiter=' ' )
                writer = csv.writer(wrfile)
                writer.writerow( ['X','Y','Z'])

                next(reader)
                for row in reader:
                    newRow = []
                    for word in row:
                        if word != '':
                            newRow.append(word)

                    newRow[0] = (float(newRow[0])-0.25) *self.chord
                    newRow[1] = (float(newRow[1]))      *self.chord
                    newRow.append(0.0)
                    writer.writerow(newRow)




    # Getters
    def getXYZ(self):
        return self.xyz
    
    def getChord(self):
        return self.chord
    
    def getAinc(self):
        return self.ainc
    
    def getAfilenameCSV(self):
        return self.afilenameCSV
        
    def getChord(self):
        return self.chord
        
    
    
                   
