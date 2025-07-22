# # Task 1 f, Calculating reserve factors against column buckling using Euler-Johnson

# ## We need from the data file:
# - volume of the element
# - Iyy calculated with `height_str, width_str, thickness_web, thickness_flange, thickness_skin, stringer_pitch`
# - dimensions
# - `EulerJohnson(EModulus, I_y, area, length, height_str, thickness_flange, thickness_web, radius, sigma_yield, sigma_applied, c=1)`

# ## Imports
import pandas as pd
import numpy as np
import sys 
import os
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../formulas'))

from formulas.columnbuckling import *
from formulas.panels import *
from formulas.helpers import *
from formulas.abd_matrix import * 

with open(os.path.join("name.txt"), "r") as f:
    name = f.read().strip()


rounding_digits = 3

# ## Constants
personal_data = personal_data_provider(name)
E_11 = personal_data[0]
E_22 = personal_data[1]
G_12 = personal_data[2]
nu_12 = personal_data[3]
sigma_u_c = 650
knockdown = 0.9
print(f"Your personal data is: E11 = {E_11}, E22 = {E_22}, G12 = {G_12}, nu12 = {nu_12}. Please verify.")

#Stacking sequences
panelStack=[45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]
StringerFlange=[45,45,-45,-45,0,0,90,90,90,90,0,0,-45,-45,45,45]
StringerWeb=[-45,-45,45,45,0,0,90,90,90,90,0,0,45,45,-45,-45]

#Ply thicknesses
tPanel = 0.552
tStringer = 0.25

#Laminate thickness
skinThickness = 8.832
flangeThickness = 4
webThickness = 4

#Geometric dimensions 
stringer_pitch = 400
effective_width = stringer_pitch/2
panelwidth = 200

panel_element_length = 250
stringer_element_length = 250


# # Here we need to calculate the necessary ABD information
# Get ABD matrix information 
ABD_panel, ABD_panel_inverse = calculateABD(stacksequence=panelStack, plyT=tPanel, EModulus1=E_11, EModulus2=E_22, ShearModulus=G_12)
ABD_flange, ABD_flange_inverse = calculateABD(stacksequence=StringerFlange, plyT=tStringer, EModulus1=E_11, EModulus2=E_22, ShearModulus=G_12)
ABD_web, ABD_web_inverse = calculateABD(stacksequence=StringerWeb, plyT=tStringer, EModulus1=E_11, EModulus2=E_22, ShearModulus=G_12)

ABD_panel = ABD_panel * knockdown
ABD_panel_inverse = ABD_panel_inverse * knockdown

ABD_flange = ABD_flange * knockdown
ABD_flange_inverse = ABD_flange_inverse * knockdown

ABD_web = ABD_web * knockdown
ABD_web_inverse = ABD_web_inverse * knockdown
#Compute necessary axial Moduli 
E_x_skin = ABD_panel[0][0]/skinThickness
E_x_flange = ABD_flange[0][0]/flangeThickness
E_x_web = 1/(ABD_web_inverse[0][0]*webThickness)


#Compute necessary bending around y Moduli 
E_y_skin = ABD_panel[3][3] *12/skinThickness**3
E_y_flange = ABD_flange[3][3]*12/flangeThickness**3
E_y_web = E_x_web


# # Importing necessary files 

# ## Import everything for panels 

# Import panel properties and match the elements to the respective panel
paneldf = pd.read_csv(f'data/{name}/panel.csv')
thickness = [8.832]* len(paneldf)
paneldf['thickness'] = thickness
paneldf = paneldf.rename(columns={'Elements':'Element ID', 'XX':'sigmaXX', 'Loadcase':'Load Case'})
paneldf['Component Name'] = paneldf.apply(elementComponentMatch, axis=1)
#panelPropertiesdf = pd.read_csv(f'../data/{name}/properties/panel_properties.csv', index_col=0)
#panelPropertiesdf = panelPropertiesdf.drop(['mass', 'Component Name'], axis=1)
#paneldf = pd.merge(paneldf, panelPropertiesdf, on='Element ID', how='left', suffixes=('_caller', '_other'))
paneldf = paneldf.drop(['XY', 'YY', 'Layer', 'Step', 'FileID'], axis=1)
paneldf.head(5)


# ## Add a volume column to the panels

paneldf['Volume'] = paneldf.apply(panel_element_volume, elementLength=panel_element_length, elementWidth=panelwidth, axis=1)
paneldf


# ## Extract thicknesses left and right 

leftThickness = []
rightThickness = []
for i in range(0,4):
    leftThickness.append(paneldf['thickness'][0+3*i])
    rightThickness.append(paneldf['thickness'][6+3*i])
print(leftThickness)
print(rightThickness)


# ## Import everything for stringers

# Open and match stringer properties 
stringerdf = pd.read_csv(f'data/{name}/stringer.csv')
stringerdf = stringerdf.rename(columns={'Elements':'Element ID', 'Element Stresses (1D):CBAR/CBEAM Axial Stress':'sigmaXX', 'Loadcase':'Load Case'})
stringerdf['Component Name'] = stringerdf.apply(elementComponentMatch, axis=1)
dflength = len(stringerdf)
stringerdf['dim1'] = [70] * dflength
stringerdf['dim2'] = [44] * dflength
stringerdf['dim3'] = [4] * dflength
stringerdf['dim4'] = [4] * dflength
# Now add the stringer properties '../data/{name}/stringer_properties.csv
#stringerPropertiesdf = pd.read_csv(f'../data/{name}/properties/stringer_properties.csv', index_col=0)
#stringerPropertiesdf = stringerPropertiesdf.reset_index()
#stringerPropertiesdf.rename(columns={'beamsects': 'Component Name', 'beamsect_dim1': 'dim1', 'beamsect_dim2': 'dim2', 'beamsect_dim3': 'dim3', 'beamsect_dim4': 'dim4'}, inplace=True)
# Add "stringer" prefix to Component Name
#stringerPropertiesdf['Component Name'] = 'stringer' + stringerPropertiesdf['Component Name'].astype(str)
# Merge the dataframes
#stringerdf = pd.merge(stringerdf, stringerPropertiesdf, on='Component Name', how='left', suffixes=('_caller', '_other'))
stringerdf = stringerdf.drop(['FileID', 'Step', ], axis=1)


# ## Add volume to the stringer elements
stringerdf['Volume']= stringerdf.apply(stringer_element_volume, elementLength = stringer_element_length, axis=1)

# # Now we rearrange the structure a bit

# ## First we split the 3 loadcases 

loadCase1dfPanel = paneldf[paneldf["Load Case"] == 1]
loadCase2dfPanel = paneldf[paneldf["Load Case"] == 2]
loadCase3dfPanel = paneldf[paneldf["Load Case"] == 3]
loadCase1dfStringer = stringerdf[stringerdf["Load Case"] == 1]
loadCase2dfStringer = stringerdf[stringerdf["Load Case"] == 2]
loadCase3dfStringer = stringerdf[stringerdf["Load Case"] == 3]


# # Now we need to combine the panels and the stringers

# For every loadcase
# Efficiently combine panels for load case 1 
panel_groups_1 = []
for i in range(1, 5):
    df1 = loadCase1dfPanel[loadCase1dfPanel['Component Name'] == f'panel{i}'].copy()
    df1 = df1[df1['Element ID'].isin(np.arange(df1['Element ID'].min()+3, df1['Element ID'].min()+6))]
    df2 = loadCase1dfPanel[loadCase1dfPanel['Component Name'] == f'panel{i+1}'].copy()
    df2 = df2[df2['Element ID'].isin(np.arange(df2['Element ID'].min(), df2['Element ID'].min()+3))]
    df3 = loadCase1dfStringer[loadCase1dfStringer['Component Name']==f'stringer{i}'].copy()
    df1['Stiffener'] = 'stiffener'+str(i)
    df2['Stiffener'] = 'stiffener'+str(i)
    df3['Stiffener'] = 'stiffener'+str(i)
    panel_groups_1.extend([df1, df2, df3])
lc1combined = pd.concat(panel_groups_1, ignore_index=True)


# Efficiently combine panels for load case 2
panel_groups_2 = []
for i in range(1, 5):
    df1 = loadCase2dfPanel[loadCase2dfPanel['Component Name'] == f'panel{i}'].copy()
    df1 = df1[df1['Element ID'].isin(np.arange(df1['Element ID'].min()+3, df1['Element ID'].min()+6))]
    df2 = loadCase2dfPanel[loadCase2dfPanel['Component Name'] == f'panel{i+1}'].copy()
    df2 = df2[df2['Element ID'].isin(np.arange(df2['Element ID'].min(), df2['Element ID'].min()+3))]
    df3 = loadCase2dfStringer[loadCase2dfStringer['Component Name']==f'stringer{i}'].copy()
    df1['Stiffener'] = 'stiffener'+str(i)
    df2['Stiffener'] = 'stiffener'+str(i)
    df3['Stiffener'] = 'stiffener'+str(i)
    panel_groups_2.extend([df1, df2, df3])
lc2combined = pd.concat(panel_groups_2, ignore_index=True)

# Efficiently combine panels for load case 3 
panel_groups_3 = []
for i in range(1, 5):
    df1 = loadCase3dfPanel[loadCase3dfPanel['Component Name'] == f'panel{i}'].copy()
    df1 = df1[df1['Element ID'].isin(np.arange(df1['Element ID'].min()+3, df1['Element ID'].min()+6))]
    df2 = loadCase3dfPanel[loadCase3dfPanel['Component Name'] == f'panel{i+1}'].copy()
    df2 = df2[df2['Element ID'].isin(np.arange(df2['Element ID'].min(), df2['Element ID'].min()+3))]
    df3 = loadCase3dfStringer[loadCase3dfStringer['Component Name']==f'stringer{i}'].copy()
    df1['Stiffener'] = 'stiffener'+str(i)
    df2['Stiffener'] = 'stiffener'+str(i)
    df3['Stiffener'] = 'stiffener'+str(i)
    panel_groups_3.extend([df1, df2, df3])
lc3combined = pd.concat(panel_groups_3, ignore_index=True)

# We fill the empty spaces with zero
lc1combined = lc1combined.fillna(0)
lc2combined = lc2combined.fillna(0)
lc3combined = lc3combined.fillna(0)

# # Now we can aggregate the loadcases according to stiffeners

# ## Multiply volume and stress together for averaging 

lc1combined['XX * Volume'] = lc1combined['sigmaXX'] * lc1combined['Volume']
lc2combined['XX * Volume'] = lc2combined['sigmaXX'] * lc2combined['Volume']
lc3combined['XX * Volume'] = lc3combined['sigmaXX'] * lc3combined['Volume']


# ## Load case 1 

lc1combined = lc1combined.groupby('Stiffener').agg({
    'XX * Volume':'sum',
    'Volume':'sum',
    'dim1': 'max',
    'dim2': 'max',
    'dim3': 'max',
    'dim4': 'max',
})
lc1combined['sigma_XX_avg'] = lc1combined['XX * Volume'] / lc1combined['Volume']
lc1combined['tLeft'] = leftThickness
lc1combined['tRight'] = rightThickness
lc1combined = lc1combined.drop(['XX * Volume'], axis=1)


# ## Load case 2
lc2combined = lc2combined.groupby('Stiffener').agg({
    'XX * Volume':'sum',
    'Volume':'sum',
    'dim1': 'max',
    'dim2': 'max',
    'dim3': 'max',
    'dim4': 'max',
})
lc2combined['sigma_XX_avg'] = lc2combined['XX * Volume'] / lc2combined['Volume']
lc2combined = lc2combined.drop(['XX * Volume'], axis=1)
lc2combined['tLeft'] = leftThickness
lc2combined['tRight'] = rightThickness
lc2combined


# ## Load case 3

lc3combined = lc3combined.groupby('Stiffener').agg({
    'XX * Volume':'sum',
    'Volume':'sum',
    'dim1': 'max',
    'dim2': 'max',
    'dim3': 'max',
    'dim4': 'max',
})
lc3combined['sigma_XX_avg'] = lc3combined['XX * Volume'] / lc3combined['Volume']
lc3combined = lc3combined.drop(['XX * Volume'], axis=1)
lc3combined['tLeft'] = leftThickness
lc3combined['tRight'] = rightThickness

# # Now we add Cross-Section Properties of the combined skin and hat stringer crosssection 
# Load case 1
lc1combined[['I_yy', 'areaTot', 'EI_comb', 'E_y_comb', 'z_bar']] = lc1combined.apply(crosssectional_properties_tee_skin_row, stringer_pitch=stringer_pitch,
                                                                    E_x_skin=E_x_skin, E_x_flange=E_x_flange, E_x_web=E_x_web,
                                                                    E_y_skin=E_y_skin, E_y_flange=E_y_flange, E_y_web=E_y_web,
                                                                    axis=1, result_type='expand')
# Load case 2
lc2combined[['I_yy', 'areaTot', 'EI_comb', 'E_y_comb', 'z_bar']] = lc2combined.apply(crosssectional_properties_tee_skin_row, stringer_pitch=stringer_pitch,
                                                                    E_x_skin=E_x_skin, E_x_flange=E_x_flange, E_x_web=E_x_web,
                                                                    E_y_skin=E_y_skin, E_y_flange=E_y_flange, E_y_web=E_y_web,
                                                                    axis=1, result_type='expand')
# Load case 3
lc3combined[['I_yy', 'areaTot', 'EI_comb', 'E_y_comb', 'z_bar']] = lc3combined.apply(crosssectional_properties_tee_skin_row, stringer_pitch=stringer_pitch,
                                                                    E_x_skin=E_x_skin, E_x_flange=E_x_flange, E_x_web=E_x_web,
                                                                    E_y_skin=E_y_skin, E_y_flange=E_y_flange, E_y_web=E_y_web,
                                                                    axis=1, result_type='expand')


# # Now we calculate the columnbuckling with Euler Johnson 

# Load case 1EModulus, DIM1, DIM2, DIM3, sigma_yield, r
lc1combined['sigma_crip'] = lc1combined.apply(lambda row: sigma_crip(sigma_u_c=sigma_u_c, DIM2=row['dim2'], DIM3=row['dim3'],DIM4=row['dim4'], r=0 ),
                                                axis=1)
# Load case 2
lc2combined['sigma_crip'] = lc2combined.apply(lambda row: sigma_crip(sigma_u_c=sigma_u_c, DIM2=row['dim2'], DIM3=row['dim3'],DIM4=row['dim4'], r=0 ),
                                                axis=1)
#Load case 3
lc3combined['sigma_crip'] = lc3combined.apply(lambda row: sigma_crip(sigma_u_c=sigma_u_c, DIM2=row['dim2'], DIM3=row['dim3'],DIM4=row['dim4'], r=0 ),
                                                axis=1)


# ## Add lambda_crit to the loadcases
lc1combined['lambda_crit'] = lc1combined.apply(lambda row: lambda_crit(EModulus=row['E_y_comb'], sigma_crip=row['sigma_crip']), axis=1)
lc2combined['lambda_crit'] = lc2combined.apply(lambda row: lambda_crit(EModulus=row['E_y_comb'], sigma_crip=row['sigma_crip']), axis=1)
lc3combined['lambda_crit'] = lc3combined.apply(lambda row: lambda_crit(EModulus=row['E_y_comb'], sigma_crip=row['sigma_crip']), axis=1)


# ## Add lambda to the loadcases
lc1combined['lambda'] = lc1combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)
lc2combined['lambda'] = lc2combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)
lc3combined['lambda'] = lc3combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)


# ## Add radius of gyration to the loadcases
lc1combined['r_gyr'] = lc1combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)
lc2combined['r_gyr'] = lc2combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)
lc3combined['r_gyr'] = lc3combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)


# ## Now calculate the critical stress & Reserve Factor
lc1combined[['sigma_crit', 'Reserve Factor']] = lc1combined.apply(chooseBuckling, axis=1, result_type='expand')
lc2combined[['sigma_crit', 'Reserve Factor']] = lc2combined.apply(chooseBuckling, axis=1, result_type='expand')
lc3combined[['sigma_crit', 'Reserve Factor']] = lc3combined.apply(chooseBuckling, axis=1, result_type='expand')



# # Cleanup data for output 

# ## Drop unenessacry columns 
lc1combined = lc1combined.drop(['Volume', 'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'sigma_crit', 'E_y_comb', 'I_yy'], axis=1)
lc2combined = lc2combined.drop(['Volume',  'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'sigma_crit', 'E_y_comb', 'I_yy'], axis=1)
lc3combined = lc3combined.drop(['Volume',  'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'sigma_crit', 'E_y_comb', 'I_yy'], axis=1)

# ## ROUND & Add together the load cases 

# Rename colums for concat
lc1combined = lc1combined.rename(columns={'sigma_XX_avg':'XX_avg_LC1', 'sigma_crit':'sigma_crit_LC1', 'Reserve Factor':'RF_LC1', 'sigma_crip':'sigma_crip_LC1'})
lc2combined = lc2combined.rename(columns={'sigma_XX_avg':'XX_avg_LC2', 'sigma_crit':'sigma_crit_LC2', 'Reserve Factor':'RF_LC2', 'sigma_crip':'sigma_crip_LC2'})
lc3combined = lc3combined.rename(columns={'sigma_XX_avg':'XX_avg_LC3', 'sigma_crit':'sigma_crit_LC3', 'Reserve Factor':'RF_LC3', 'sigma_crip':'sigma_crip_LC3'})


outputdf = pd.concat([lc1combined,lc2combined,lc3combined], axis = 1)
#outputdf = outputdf.round(rounding_digits)
# After concatenation, keep only the first column of cross section propertries and drop the rest
outputdf['Lambda'] = outputdf.filter(like='lambda').iloc[:, 1]  # Take the first lambda column
outputdf['Lambda_crit'] = outputdf.filter(like='lambda_crit').iloc[:, 0]  # Take the first I_yy column
outputdf['R_gyr'] = outputdf.filter(like='r_gyr').iloc[:, 0]  # Take the first I_yy column
outputdf['EI_Comb'] = outputdf.filter(like='EI_comb').iloc[:, 0]  # Take the first I_yy column
outputdf['z_EC,comb'] = outputdf.filter(like='z_bar').iloc[:, 0]  # Take the first I_yy column
outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('lambda')])
outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('r_gyr')])
outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('EI_comb')])
outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('z_bar')])



# ## Add other requested values 
outputLength = len(outputdf)
outputdf['E_hom,b,flange'] = [E_y_flange] * outputLength
outputdf['E_hom,b,web'] = [E_y_web] * outputLength
outputdf['E_hom,b,skin_left'] = [E_y_skin] * outputLength
outputdf['E_hom,b,skin_right'] = [E_y_skin] * outputLength

# # Generate output file

outputdf.to_excel(f'data/{name}/output/processed_f.xlsx')