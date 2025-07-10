# Calculating the reserve Factors of the panels 
# # Imports

import pandas as pd
import sys 
import os
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../formulas'))
sys.path.insert(0, os.path.abspath('../optimization'))

from formulas.panels import *
from formulas.helpers import *
from formulas.abd_matrix import *

with open(os.path.join("name.txt"), "r") as f:
    name = f.read().strip()

rounding_digits = 3

# # Constants (Changed based on your data)

personal_data = personal_data_provider(name)
E_11 = personal_data[0]
E_22 = personal_data[1]
G_12 = personal_data[2]
nu_12 = personal_data[3]
knockdown = 0.9 
print(f"Your personal data is: E11 = {E_11}, E22 = {E_22}, G12 = {G_12}, nu12 = {nu_12}. Please verify.")

# Panel laminate properties 
panelStack = [45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]
tPanel = 0.552 

#Panel constants 
length = 750
width = 400
panelthickness = 8.832


# # Import needed ABD values 

ABD_panel, ABD_panel_inverse = calculateABD(stacksequence=panelStack, plyT=tPanel, EModulus1=E_11, EModulus2=E_22, ShearModulus=G_12)
ABD_panel = ABD_panel * knockdown
ABD_panel_inverse = ABD_panel_inverse * knockdown


# ## Extract ABD parameters 


D11 = ABD_panel[3][3]
D22 = ABD_panel[4][4]
D12 = ABD_panel[3][4]
D66 = ABD_panel[5][5]
print(D11, D22, D12, D66)


# # Open stress values & properties of panels


# New version of importing panel stress file
paneldf = pd.read_csv(f'data/{name}/panel.csv')
paneldf = paneldf.rename(columns={'Elements':'Element ID', 'XX':'sigmaXX', 'YY':'sigmaYY', 'XY':'sigmaXY', 'Loadcase':'Load Case'})
paneldf['Component Name'] = paneldf.apply(elementComponentMatch, axis=1)
paneldf = paneldf.drop(['FileID', 'Step', 'Layer'], axis=1)
paneldf.head(5)


# # Split up the loadcases
loadCase1df = paneldf[paneldf['Load Case'] == 1]
loadCase2df = paneldf[paneldf['Load Case'] == 2]
loadCase3df = paneldf[paneldf['Load Case'] == 3]


#Set index back to Element ID 
loadCase1df = loadCase1df.set_index('Element ID')
loadCase2df = loadCase2df.set_index('Element ID')
loadCase3df = loadCase3df.set_index('Element ID')


# # Now we need to combine into panels:
# -Panel ID (as our ID)
# -sigmaXXavg
# -sigmaYYavg
# -sigmaXYavg
# -length
# -width
# -thickness 
# 


# We can just average the stresses @fabianober Tackle rounding!!!! 
#For load case 1 
panelLC1 = loadCase1df.groupby('Component Name').agg({
    'sigmaXX': 'mean',
    'sigmaYY':'mean',
    'sigmaXY':'mean',
})
dataframeLength = len(panelLC1)
panelLC1['length'] = [length]*dataframeLength
panelLC1['width'] = [width]*dataframeLength
panelLC1['thickness'] = [panelthickness] * dataframeLength
panelLC1['Load Case'] = ['LC1'] * dataframeLength

#For load case 2 
panelLC2 = loadCase2df.groupby('Component Name').agg({
    'sigmaXX': 'mean',
    'sigmaYY':'mean',
    'sigmaXY':'mean'
})
dataframeLength = len(panelLC2)
panelLC2['length'] = [length]*dataframeLength
panelLC2['width'] = [width]*dataframeLength
panelLC2['thickness'] = [panelthickness] * dataframeLength
panelLC2['Load Case'] = ['LC2'] * dataframeLength

#For load case 3
panelLC3 = loadCase3df.groupby('Component Name').agg({
    'sigmaXX': 'mean',
    'sigmaYY':'mean',
    'sigmaXY':'mean'
})
dataframeLength = len(panelLC3)
panelLC3['length'] = [length]*dataframeLength
panelLC3['width'] = [width]*dataframeLength
panelLC3['thickness'] = [panelthickness] * dataframeLength
panelLC3['Load Case'] = ['LC3'] * dataframeLength


# # Now we can apply the functions to the load cases 

panelLC1[['sig_crit_shear', 'sig_crit_biax', 'Reserve Factor']] = panelLC1.apply(panelBuckApply, D11=D11, D12=D12, D22=D22,
                                                                                  D66=D66, axis=1, result_type='expand')
panelLC2[['sig_crit_shear', 'sig_crit_biax', 'Reserve Factor']] = panelLC2.apply(panelBuckApply, D11=D11, D12=D12, D22=D22,
                                                                                  D66=D66, axis=1, result_type='expand')
panelLC3[['sig_crit_shear', 'sig_crit_biax', 'Reserve Factor']] = panelLC3.apply(panelBuckApply, D11=D11, D12=D12, D22=D22,
                                                                                  D66=D66, axis=1, result_type='expand')

# # Create original output

#Drop irrelevant columns
panelLC1 = panelLC1.drop(['length', 'width', 'thickness', 'Load Case'], axis=1)
panelLC2 = panelLC2.drop(['length', 'width',  'thickness', 'Load Case'], axis=1)
panelLC3 = panelLC3.drop(['length', 'width',  'thickness', 'Load Case'], axis=1)

# Rename columns to be unambigous
panelLC1 = panelLC1.rename(columns={"Reserve Factor": "LC 1 RF", 'sigmaXX':'sigmaXXLC1', 'sigmaYY':'sigmaYYLC1', 'sigmaXY':'sigmaXYLC1', 'sig_crit_shear':'sig_crit_shearLC1', 'sig_crit_biax':'sig_crit_biaxLC1'})
panelLC2 = panelLC2.rename(columns={"Reserve Factor": "LC 2 RF", 'sigmaXX':'sigmaXXLC2', 'sigmaYY':'sigmaYYLC2', 'sigmaXY':'sigmaXYLC2', 'sig_crit_shear':'sig_crit_shearLC2', 'sig_crit_biax':'sig_crit_biaxLC2'})
panelLC3 = panelLC3.rename(columns={"Reserve Factor": "LC 3 RF", 'sigmaXX':'sigmaXXLC3', 'sigmaYY':'sigmaYYLC3', 'sigmaXY':'sigmaXYLC3', 'sig_crit_shear':'sig_crit_shearLC3', 'sig_crit_biax':'sig_crit_biaxLC3'})

outputDf = pd.concat([panelLC1, panelLC2, panelLC3], axis=1)
outputDf


# # ROUND & Output the files

outputDf = outputDf.round(rounding_digits)
outputDf.to_excel(f'data/{name}/output/processed_e.xlsx')
outputDf.head(10)

