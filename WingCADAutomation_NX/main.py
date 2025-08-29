# Filename: main.py
# Author: Jose Camino-Cantu
# Date: 2025-08-3
# Version: 1.0
# Description: This script takes an input AVL geometry file and builds CAD geoemtry in Siemens NX

import os
import sys
import math
from WingClass import Wing


def main():

    #Inputs
    filename = "N:\windat.v2\Documents\Projects\QuickBuild\TestFolder\QuickBuild-1.txt"
    projectName= 'test'                         # used for naming .dat files
    numSects = 3                                # number of sections in AVL Wing
    
    #Run
    wingData = Wing(numSects,projectName)
    wingData.getData(filename)
    wingData.buildGeo()

    

    
# namegaurd
if __name__ == "__main__":
    main()
