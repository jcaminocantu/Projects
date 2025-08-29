
QuickBuild - AVL-to-NX Wing CAD Generator

Author: Jose Camino-Cantu, University of Michigan Aerospace Engineering Student
Date: August 3, 2025
Version: 1


Overview:
This project converts an AVL geometry file into a CAD model in Siemens NX using the NX Open API.


AVL Geometry Input:
Program requires an AVL geometry file (whether .txt or .avl) with only one defined surface.
QuickBuild parses through the AVL file and identifies relevant wing geometry including: 
-Surface Angle
-Section Angle (relative to surface)
-Section Airfoil
-Section Leading Edge Position
-Section Chord

Limitations: 
-will not work with various Surfaces defined or incorrect AVL syntax
-cannot model dihedral 
-cannot add wing to existing 
-can only model right wing, but can be mirrored in NX after the fact

Note:
While QuickBuild will work within an existing .prt file, recommend creating a new file and later importing into desired location. 

Workflow:

1 - Prepare AVL file containing Wing Geometry
2 - Enable NX Open Developer
	i - Windows -> Edit Environment Variables for your Account 
	ii - New -> Variable Name: NX_DEVELOPER, Variable Value: 1
	iii - Ok

3 - Open Siemens NX, navigate to desired .prt file
4 - Navigate to Edit Journal using the search bar
5 - Edit filename, projectName, and numSects variables with relevant values
6 - Click Play Journal 