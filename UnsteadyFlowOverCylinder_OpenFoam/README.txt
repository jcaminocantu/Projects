
Unsteady Flow over a Cylinder.

Performed at Re=80, CFL_max = 0.89
Results: Cd = 1.08, St = 0.163, 

This project marks my graduation from OpenFoam tutorials and creating my first simulation from scratch. 
Furthermore, this is my first venture away from steady-state into unsteady flow, resulting in a lot of learning of timestep requirements for adequate CFL. Similarly, I familiarized myself with ParaView, specifically with how to extract force coefficients. 

Mesh was created using blockMesh, with the overall design  adapted from "Unsteady Simulations of Flow Around a Smooth Circular Cylinder at Very High Reynolds Numbers" by Andrew Porteous. 

Although it was a laminar simulation and this no wall functions were utilized, initial mesh size was determined to achieve a y+ ~= 1 as an upperbound, then further refined. 

Overall, I am happy with the results, achieving agreement within 10% of literature.
