#!/usr/bin/env python
# coding: utf-8

# # Stress analysis for each element

# # Import modules 
import pandas as pd
import sys 
import os
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../formulas'))

from formulas.panels import *
from formulas.helpers import *
from formulas.abd_matrix import *
from formulas.Strength import * 

with open(os.path.join("name.txt"), "r") as f:
    name = f.read().strip()

# # Import needed files 
# ## Import panel stresses
PlyStressesX = pd.read_csv(f'data/{name}/compositePanelXX.csv')
PlyStressesX = PlyStressesX.drop(columns=['FileID', 'Step'])
PlyStressesY = pd.read_csv(f'data/{name}/compositePanelYY.csv')
PlyStressesY = PlyStressesY.drop(columns=['FileID', 'Step'])
PlyStressesXY = pd.read_csv(f'data/{name}/compositePanelXY.csv')
PlyStressesXY = PlyStressesXY.drop(columns=['FileID', 'Step'])

PlyStressesPanel=pd.merge(PlyStressesX,PlyStressesY, on=['Elements', 'Layer', 'Loadcase'])
PlyStressesPanel = pd.merge(PlyStressesPanel, PlyStressesXY, on=['Elements', 'Layer', 'Loadcase'])
PlyStressesPanel = PlyStressesPanel.rename(columns={'Composite Stresses:Normal X Stress':'Normal_1', 'Composite Stresses:Normal Y Stress':'Normal_2', 'Composite Stresses:Shear XY Stress':'Shear_12' })



# ## Import stringer plies

StringerStrains = pd.read_csv(f'data/{name}/stringer_strain.csv')
StringerStrains = StringerStrains.drop(columns=['FileID', 'Step'])
StringerStrains = StringerStrains.rename(columns={'Element Strains (1D):CBAR/CBEAM Axial Strain':'strainX'})

# Constants for analysis


# r = perpendicular 
# p = parallel
# c = compression 
# t = tension 
# Resistance values 

R_p_t = 3050
R_p_c = 1500
R_r_c = 50
R_r_t = 300 
R_rp = 100

# p values 
# Perpendicular, parallel
p_rp_c = 0.25
p_rp_t = 0.25

# Perpendicular, perpendicular
p_rr_c = 0.25
p_rr_t = 0.25

#Ply orientation in flange 
StringerFlange=[45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]


# # Personal data Provider


personal_data = personal_data_provider(name)
E_11 = personal_data[0]
E_22 = personal_data[1]
G_12 = personal_data[2]
nu_12 = personal_data[3]


# # Calculate RF and mode for panels

PlyStressesPanel['Normal_1'] = PlyStressesPanel['Normal_1'] * 1.5 # encorporate 1.5 for ultimate loads
PlyStressesPanel['Normal_2'] = PlyStressesPanel['Normal_2'] * 1.5
PlyStressesPanel['Shear_12'] = PlyStressesPanel['Shear_12'] * 1.5

PlyStressesPanel[['Mode', 'RF_IFF', 'RF_FF']] = PlyStressesPanel.apply(strength, R_p_t=R_p_t, R_p_c=R_p_c, R_r_c=R_r_c, R_r_t=R_r_t, 
                                                    R_rp=R_rp, p_rp_c=p_rp_c, p_rp_t=p_rp_t, p_rr_c=p_rr_c, p_rr_t=p_rr_t,
                                                    axis=1, result_type='expand')


# ## Calculate RF_strength 
PlyStressesPanel['RF_strength'] = PlyStressesPanel[['RF_IFF', 'RF_FF']].min(axis=1)

# ## Convert to output for panels 
# We can drop the stresses 
PlyStressesPanel = PlyStressesPanel.drop(columns=['Normal_1', 'Normal_2', 'Shear_12'])

#Reorder plies 
PlyStressesPanel['Layer_num'] = PlyStressesPanel['Layer'].str.extract(r'(\d+)').astype(int)
PlyStressesPanel = PlyStressesPanel.sort_values(by='Layer_num')
PlyStressesPanel = PlyStressesPanel.drop(columns=['Layer'])
PlyStressesPanel = PlyStressesPanel.rename(columns={'Layer_num':'Layer'})

# Resort columns to desired order
PlyStressesPanel = PlyStressesPanel[['Elements', 'Layer', 'Loadcase', 'RF_FF', 'RF_IFF', 'Mode', 'RF_strength']]

# We need to analyse element 8 
PlyStressesPanel = PlyStressesPanel[PlyStressesPanel['Elements'] == 8]
#Now we separate the loadcases 
PlyStressesPanelLC1 = PlyStressesPanel[PlyStressesPanel['Loadcase'] == 1]
PlyStressesPanelLC2 = PlyStressesPanel[PlyStressesPanel['Loadcase'] == 2]
PlyStressesPanelLC3 = PlyStressesPanel[PlyStressesPanel['Loadcase'] == 3]

# ## Rename Loadcases 
# # Loadcase 1
PlyStressesPanelLC1 = PlyStressesPanelLC1.rename(columns={'RF_FF':'R_FF_LC1', 'RF_IFF':'R_IFF_LC1', 'Mode':'Mode_LC1', 'RF_strength':'RF_strength_LC1'})
PlyStressesPanelLC1 = PlyStressesPanelLC1.reset_index()
PlyStressesPanelLC1 = PlyStressesPanelLC1.drop(columns=['index', 'Loadcase'])

# Loadcase 2
PlyStressesPanelLC2 = PlyStressesPanelLC2.rename(columns={'RF_FF':'R_FF_LC2', 'RF_IFF':'R_IFF_LC2', 'Mode':'Mode_LC2', 'RF_strength':'RF_strength_LC2'})
PlyStressesPanelLC2 = PlyStressesPanelLC2.reset_index()
PlyStressesPanelLC2 = PlyStressesPanelLC2.drop(columns=['index', 'Loadcase'])

#Loadcase 3 
PlyStressesPanelLC3 = PlyStressesPanelLC3.rename(columns={'RF_FF':'R_FF_LC3', 'RF_IFF':'R_IFF_LC3', 'Mode':'Mode_LC3', 'RF_strength':'RF_strength_LC3'})
PlyStressesPanelLC3 = PlyStressesPanelLC3.reset_index()
PlyStressesPanelLC3 = PlyStressesPanelLC3.drop(columns=['index', 'Loadcase'])


# Combine Loadcases
PlyStressesPanel = PlyStressesPanelLC1.merge(PlyStressesPanelLC2, on=['Elements', 'Layer'], suffixes=('_LC1', '_LC2'))
PlyStressesPanel = PlyStressesPanel.merge(PlyStressesPanelLC3, on=['Elements', 'Layer'])


# # Output panel


PlyStressesPanel.to_excel(f'data/{name}/output/panelStrength.xlsx')


# # Calculate stringer strength
# ## Expand the dataframe 

# Create a DataFrame with PlyNumber 1-16
ply_numbers = pd.DataFrame({'PlyNumber': np.arange(1, 17),
                            'plyTheta': StringerFlange})

# Cross join to expand each element row to 16 plies
StringerStrains = StringerStrains.merge(ply_numbers, how='cross')
#StringerStrains = StringerStrains.drop(columns=['PlyNumber_x'])

StringerStrains[['Normal_1', 'Normal_2', 'Shear_12']] = StringerStrains.apply(
    calculateMatStress, EModulus1=E_11, EModulus2=E_22, ShearModulus=G_12, axis=1,
    result_type='expand'
)


# ## Now calculate the FF and the IFF 

# Ultimate load factor
StringerStrains['Normal_1'] = StringerStrains['Normal_1'] * 1.5 # encorporate 1.5 for ultimate loads
StringerStrains['Normal_2'] = StringerStrains['Normal_2'] * 1.5
StringerStrains['Shear_12'] = StringerStrains['Shear_12'] * 1.5


StringerStrains[['Mode', 'RF_IFF', 'RF_FF']] = StringerStrains.apply(strength, R_p_t=R_p_t, R_p_c=R_p_c, R_r_c=R_r_c, R_r_t=R_r_t, 
                                                    R_rp=R_rp, p_rp_c=p_rp_c, p_rp_t=p_rp_t, p_rr_c=p_rr_c, p_rr_t=p_rr_t,
                                                    axis=1, result_type='expand')
StringerStrains['RF_strength'] = StringerStrains[['RF_IFF', 'RF_FF']].min(axis=1)

# We can drop the stresses 
StringerStrains = StringerStrains.drop(columns=['Normal_1', 'Normal_2', 'Shear_12','strainX', 'plyTheta'])

# Resort columns to desired order
StringerStrains = StringerStrains[['Elements', 'PlyNumber', 'Loadcase', 'RF_FF', 'RF_IFF', 'Mode', 'RF_strength']]

# We need to analyse element 8 
StringerStrains = StringerStrains[StringerStrains['Elements'] == 60]
#Now we separate the loadcases 
PlyStressesStringerLC1 = StringerStrains[StringerStrains['Loadcase'] == 1]
PlyStressesStringerLC2 = StringerStrains[StringerStrains['Loadcase'] == 2]
PlyStressesStringerLC3 = StringerStrains[StringerStrains['Loadcase'] == 3]


# ## Rename Loadcases 

# Loadcase 1
PlyStressesStringerLC1 = PlyStressesStringerLC1.rename(columns={'RF_FF':'R_FF_LC1', 'RF_IFF':'R_IFF_LC1', 'Mode':'Mode_LC1', 'RF_strength':'RF_strength_LC1'})
PlyStressesStringerLC1 = PlyStressesStringerLC1.reset_index()
PlyStressesStringerLC1 = PlyStressesStringerLC1.drop(columns=['index', 'Loadcase'])

# Loadcase 2
PlyStressesStringerLC2 = PlyStressesStringerLC2.rename(columns={'RF_FF':'R_FF_LC2', 'RF_IFF':'R_IFF_LC2', 'Mode':'Mode_LC2', 'RF_strength':'RF_strength_LC2'})
PlyStressesStringerLC2 = PlyStressesStringerLC2.reset_index()
PlyStressesStringerLC2 = PlyStressesStringerLC2.drop(columns=['index', 'Loadcase'])

#Loadcase 3 
PlyStressesStringerLC3 = PlyStressesStringerLC3.rename(columns={'RF_FF':'R_FF_LC3', 'RF_IFF':'R_IFF_LC3', 'Mode':'Mode_LC3', 'RF_strength':'RF_strength_LC3'})
PlyStressesStringerLC3 = PlyStressesStringerLC3.reset_index()
PlyStressesStringerLC3 = PlyStressesStringerLC3.drop(columns=['index', 'Loadcase'])

# ## Combine Loadcases 

PlyStressesStringer = PlyStressesStringerLC1.merge(PlyStressesStringerLC2, on=['Elements', 'PlyNumber'], suffixes=('_LC1', '_LC2'))
PlyStressesStringer = PlyStressesStringer.merge(PlyStressesStringerLC3, on=['Elements', 'PlyNumber'])

# ## Output stringer

PlyStressesStringer.to_excel(f'data/{name}/output/stringerStrength.xlsx')