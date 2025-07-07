import sys
import os
import random
import string
import json

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('hmscript'))
sys.path.insert(0, os.path.abspath('formulas'))
sys.path.insert(0, os.path.abspath('calculators'))

from abd_matrix import *


print("Starting analysis...")

with open('data.json', 'r') as f:
    personal_data = json.load(f)

name = personal_data.get("name")
E_11_avg = personal_data.get("E_11_avg")
E_22_avg = personal_data.get("E_22_avg")
G_12_avg = personal_data.get("G_12_avg")

print(f"Your data is: Name: {name}, E_11_avg: {E_11_avg}, E_22_avg: {E_22_avg}, G_12_avg: {G_12_avg}")

'Start by defining some of the necessary dimensions'
#Stacking sequences 
panelStack=[45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]
StringerFlange=[45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]
StringerWeb=[-45,-45,45,45,0,0,90,90,90,90,0,0,45,45,-45,-45]

#Ply thicknesses 
tPanel = 0.552
tStringer = 0.25

ABD_panel, ABD_panel_inverse = calculateABD(stacksequence=panelStack, plyT=tPanel, EModulus1=E_11_avg, EModulus2=E_22_avg, ShearModulus=G_12_avg)
ABD_flange, ABD_flange_inverse = calculateABD(stacksequence=StringerFlange, plyT=tStringer, EModulus1=E_11_avg, EModulus2=E_22_avg, ShearModulus=G_12_avg)
ABD_web, ABD_web_inverse = calculateABD(stacksequence=StringerWeb, plyT=tStringer, EModulus1=E_11_avg, EModulus2=E_22_avg, ShearModulus=G_12_avg)

print("ABD matrix for panel:")
for row in ABD_panel:
    print("  ".join(f"{val:10.3f}" for val in row))
print("ABD matrix for flange:")
print(ABD_flange)
print("ABD matrix for web:")
print(ABD_web)
print("Inverse ABD matrix for panel:")
print(ABD_panel_inverse)


# Calculate the homogonized average axial EModulus 
E_avg_x_web = 1/(ABD_web_inverse[0][0]*4)
A_web = 40*4
E_avg_x_flange = ABD_flange[0][0]/4
A_flange = 70*4
E_avg_x = (E_avg_x_web*A_web + E_avg_x_flange*A_flange)/(A_web+A_flange)
print('Your homogonized average Ex is: '+str(E_avg_x))



