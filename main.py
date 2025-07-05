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
print(ABD_flange)
print(ABD_web)

