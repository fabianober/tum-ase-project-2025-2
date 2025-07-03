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
from optimization.generation import *
from optimization.columnBuckReverse import *


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # Reverse Engineering part


def calculate_stringers(name, RFgoal=1):
    rounding_digits = 3

    # ## Constants
    personal_data = personal_data_provider(name)
    sigma_yield = personal_data[0]
    EModulus = personal_data[1]
    #print(f"Your personal data is: sigma_yield = {sigma_yield}, EModulus = {EModulus}. Please verify.")

    stringer_pitch = 200
    effective_width = stringer_pitch/2

    panel_element_length = 750/3
    stringer_element_length = 750/3

    # # Importing necessary files 
    # ## Import everything for panels 
    # Import panel properties and match the elements to the respective panel
    paneldf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/panel.csv'))
    panelPropertiesdf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/properties/panel_properties.csv'), index_col=0)
    panelPropertiesdf = panelPropertiesdf.drop(['mass', 'Component Name'], axis=1)
    paneldf = pd.merge(paneldf, panelPropertiesdf, on='Element ID', how='left', suffixes=('_caller', '_other'))
    paneldf = paneldf.drop(['sigmaXY', 'sigmaYY'], axis=1)
    #paneldf.head(5)

    # ## Add a volume column to the panels 
    paneldf['Volume'] = paneldf.apply(panel_element_volume, elementLength=panel_element_length, elementWidth=stringer_pitch, axis=1)

    # We now Extract thicknesses left and right !
    leftThickness = []
    rightThickness = []
    for i in range(0,9):
        leftThickness.append(paneldf['thickness'][0+3*i])
        rightThickness.append(paneldf['thickness'][3+3*i])

    # ## Import everything for stringers 
    # Open and match stringer properties 
    stringerdf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/stringer.csv'))
    # Now add the stringer properties '../data/{name}/stringer_properties.csv
    stringerPropertiesdf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/properties/stringer_properties.csv'), index_col=0)
    stringerPropertiesdf = stringerPropertiesdf.reset_index()
    stringerPropertiesdf.rename(columns={'beamsects': 'Component Name', 'beamsect_dim1': 'dim1', 'beamsect_dim2': 'dim2', 'beamsect_dim3': 'dim3', 'beamsect_dim4': 'dim4'}, inplace=True)
    # Add "stringer" prefix to Component Name
    stringerPropertiesdf['Component Name'] = 'stringer' + stringerPropertiesdf['Component Name'].astype(str)
    # Merge the dataframes
    stringerdf = pd.merge(stringerdf, stringerPropertiesdf, on='Component Name', how='left', suffixes=('_caller', '_other'))
    #stringerdf

    # ## Add volume to the stringer elements
    stringerdf['Volume']= stringerdf.apply(stringer_element_volume, elementLength = stringer_element_length, axis=1)
    #stringerdf.head(3)

    # # Now we rearrange the structure a bit
    # ## First we split the 3 loadcases
    loadCase1dfPanel = paneldf[paneldf["Load Case"] == 'Subcase 1 (LC1)']
    loadCase2dfPanel = paneldf[paneldf["Load Case"] == 'Subcase 2 (LC2)']
    loadCase3dfPanel = paneldf[paneldf["Load Case"] == 'Subcase 3 (LC3)']
    loadCase1dfStringer = stringerdf[stringerdf["Load Case"] == 'Subcase 1 (LC1)']
    loadCase2dfStringer = stringerdf[stringerdf["Load Case"] == 'Subcase 2 (LC2)']
    loadCase3dfStringer = stringerdf[stringerdf["Load Case"] == 'Subcase 3 (LC3)']
    ##print(loadCase1dfPanel.head(5))
    ##print(loadCase1dfStringer.head(5))

    # # Now we need to combine the panels and the stringers
    # For every loadcase
    # Efficiently combine panels for load case 1 
    panel_groups_1 = []
    for i in range(1, 10):
        df1 = loadCase1dfPanel[loadCase1dfPanel['Component Name'] == f'panel{i}'].copy()
        df2 = loadCase1dfPanel[loadCase1dfPanel['Component Name'] == f'panel{i+1}'].copy()
        df3 = loadCase1dfStringer[loadCase1dfStringer['Component Name']==f'stringer{i}'].copy()
        df1['Stiffener'] = 'stiffener'+str(i)
        df2['Stiffener'] = 'stiffener'+str(i)
        df3['Stiffener'] = 'stiffener'+str(i)
        panel_groups_1.extend([df1, df2, df3])
    lc1combined = pd.concat(panel_groups_1, ignore_index=True)
    #lc1combined.head(10)

    # Efficiently combine panels for load case 2
    panel_groups_2 = []
    for i in range(1, 10):
        df1 = loadCase2dfPanel[loadCase2dfPanel['Component Name'] == f'panel{i}'].copy()
        df2 = loadCase2dfPanel[loadCase2dfPanel['Component Name'] == f'panel{i+1}'].copy()
        df3 = loadCase2dfStringer[loadCase2dfStringer['Component Name']==f'stringer{i}'].copy()
        df1['Stiffener'] = 'stiffener'+str(i)
        df2['Stiffener'] = 'stiffener'+str(i)
        df3['Stiffener'] = 'stiffener'+str(i)
        panel_groups_2.extend([df1, df2, df3])
    lc2combined = pd.concat(panel_groups_2, ignore_index=True)
    #lc2combined.head(10)

    # Efficiently combine panels for load case 3 
    panel_groups_3 = []
    for i in range(1, 10):
        df1 = loadCase3dfPanel[loadCase3dfPanel['Component Name'] == f'panel{i}'].copy()
        df2 = loadCase3dfPanel[loadCase3dfPanel['Component Name'] == f'panel{i+1}'].copy()
        df3 = loadCase3dfStringer[loadCase3dfStringer['Component Name']==f'stringer{i}'].copy()
        df1['Stiffener'] = 'stiffener'+str(i)
        df2['Stiffener'] = 'stiffener'+str(i)
        df3['Stiffener'] = 'stiffener'+str(i)
        panel_groups_3.extend([df1, df2, df3])
    lc3combined = pd.concat(panel_groups_3, ignore_index=True)
    #lc3combined.head(10)

    # We fill the empty spaces with zero
    lc1combined = lc1combined.fillna(0)
    lc2combined = lc2combined.fillna(0)
    lc3combined = lc3combined.fillna(0)

    # # Now we can aggregate the loadcases according to stiffeners
    # ## Multiply volume and stress together for averaging 
    lc1combined['XX * Volume'] = lc1combined['sigmaXX'] * lc1combined['Volume']
    lc2combined['XX * Volume'] = lc2combined['sigmaXX'] * lc2combined['Volume']
    lc3combined['XX * Volume'] = lc3combined['sigmaXX'] * lc3combined['Volume']
    #lc1combined.head(2)

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
    lc1combined[['I_yy', 'areaTot', 'VolumeTot']] = lc1combined.apply(crosssectional_properties_hat_skin_row, stringer_pitch=stringer_pitch, stringer_depth = stringer_element_length*3,
                                                                        axis=1, result_type='expand')
    # Load case 2
    lc2combined[['I_yy', 'areaTot', 'VolumeTot']] = lc2combined.apply(crosssectional_properties_hat_skin_row, stringer_pitch=stringer_pitch, stringer_depth = stringer_element_length*3,
                                                                        axis=1, result_type='expand')
    # Load case 3
    lc3combined[['I_yy', 'areaTot', 'VolumeTot']] = lc3combined.apply(crosssectional_properties_hat_skin_row, stringer_pitch=stringer_pitch, stringer_depth = stringer_element_length*3,
                                                                        axis=1, result_type='expand')

    # # Now we calculate the columnbuckling with Euler Johnson 
    # Load case 1EModulus, DIM1, DIM2, DIM3, sigma_yield, r
    lc1combined['sigma_crip'] = lc1combined.apply(lambda row: sigma_crip(EModulus= EModulus, DIM1=row['dim1'], DIM2=row['dim2'], DIM3=row['dim3'], sigma_yield = sigma_yield, r=0 ),
                                                    axis=1)
    # Load case 2
    lc2combined['sigma_crip'] = lc2combined.apply(lambda row: sigma_crip(EModulus= EModulus, DIM1=row['dim1'], DIM2=row['dim2'], DIM3=row['dim3'], sigma_yield = sigma_yield, r=0 ),
                                                    axis=1)
    #Load case 3
    lc3combined['sigma_crip'] = lc3combined.apply(lambda row: sigma_crip(EModulus= EModulus, DIM1=row['dim1'], DIM2=row['dim2'], DIM3=row['dim3'], sigma_yield = sigma_yield, r=0 ),
                                                    axis=1)

    # ## Add lambda_crit to the loadcases
    lc1combined['lambda_crit'] = lc1combined.apply(lambda row: lambda_crit(EModulus, row['sigma_crip'], personal_data[0]), axis=1)
    lc2combined['lambda_crit'] = lc2combined.apply(lambda row: lambda_crit(EModulus, row['sigma_crip'], personal_data[0]), axis=1)
    lc3combined['lambda_crit'] = lc3combined.apply(lambda row: lambda_crit(EModulus, row['sigma_crip'], personal_data[0]), axis=1)

    # ## Add lambda to the loadcases
    lc1combined['lambda'] = lc1combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)
    lc2combined['lambda'] = lc2combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)
    lc3combined['lambda'] = lc3combined.apply(lambda row: lmd(row['I_yy'], row['areaTot'], stringer_element_length*3), axis=1)

    # ## Add radius of gyration to the loadcases
    lc1combined['r_gyr'] = lc1combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)
    lc2combined['r_gyr'] = lc2combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)
    lc3combined['r_gyr'] = lc3combined.apply(lambda row: r_gyr(row['I_yy'], row['areaTot']), axis=1)

    # ## Now calculate the critical stress & Reserve Factor
    lc1combined[['sigma_crit', 'Reserve Factor']] = lc1combined.apply(chooseBuckling, EModulus=EModulus, sigma_yield=sigma_yield, axis=1, result_type='expand')
    lc2combined[['sigma_crit', 'Reserve Factor']] = lc2combined.apply(chooseBuckling, EModulus=EModulus, sigma_yield=sigma_yield, axis=1, result_type='expand')
    lc3combined[['sigma_crit', 'Reserve Factor']] = lc3combined.apply(chooseBuckling, EModulus=EModulus, sigma_yield=sigma_yield, axis=1, result_type='expand')

    # # Generate Score output 
    lc1combined = lc1combined.reset_index()
    lc2combined = lc2combined.reset_index()
    lc3combined = lc3combined.reset_index()

    evaluateDf = pd.concat([lc1combined, lc2combined, lc3combined])
    evaluateDf = evaluateDf.reset_index()
    evaluateDf = evaluateDf.drop(['index'], axis=1)
    updateDF = evaluateDf.copy()
    


    evaluateDf = evaluateDf.drop(['Volume', 'tLeft', 'tRight', 'sigma_XX_avg', 'I_yy',  'areaTot', 'VolumeTot', 'sigma_crip', 'lambda_crit', 'lambda', 'r_gyr', 'sigma_crit'], axis =1)

    evaluateDf.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/StringerRFs.csv'), index=False)

    evaluateDf['score'] = evaluateDf.apply(rf_score, axis=1)

    # ## Extract score and parameters
    score = evaluateDf['score'].sum()
    dimensions = extractDimensions(evaluateDf)

    evaluateDf = pd.DataFrame({
        'stringer Parameters': [dimensions],
        'score': [score],
        'minRF':[evaluateDf['Reserve Factor'].min()]
    })

    # ## Output stringer score
    evaluateDf.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/stringerScore.csv'), index=False)
    
    
    # # Reverse Engineering
    updateDF[['new_dim1', 'new_dim3']] = updateDF.apply(reverseAllDims, EModulus=EModulus,
                                                                    stringerPitch=stringer_pitch,
                                                                    length=stringer_element_length*3,
                                                                    RFgoal=RFgoal, axis=1, result_type='expand')
    updateDF = updateDF.drop(['Volume', 'tLeft', 'tRight', 'sigma_XX_avg', 'I_yy',  'areaTot', 'VolumeTot', 'sigma_crip', 'lambda_crit', 'lambda', 'r_gyr', 'sigma_crit'], axis =1)
    # ##Keep only essential data 
    updateDF = updateDF.groupby('Stiffener').agg({
    'dim1': 'max',
    'dim2': 'max',
    'dim3': 'max',
    'dim4': 'max',
    'new_dim1': 'max',
    'new_dim3': 'max'
    #'new_dim4': 'max'
    })


    # ## Add differnces of the Stringer 
    updateDF['diff_dim1'] = (updateDF['new_dim1'] - updateDF['dim1']).astype(float)
    updateDF['diff_dim3'] = (updateDF['new_dim3'] - updateDF['dim3']). astype(float)
    #updateDF['diff_dim4'] = (updateDF['new_dim4'] - updateDF['dim4']).astype(float)

    #Convert type 
    updateDF['new_dim1'] = updateDF['new_dim1'].astype(float)
    updateDF['new_dim3'] = updateDF['new_dim3'].astype(float)
    #updateDF['new_dim4'] = updateDF['new_dim4'].astype(float)


    updateDF = updateDF.round(rounding_digits)
    # ##Output Stringer Reverse  
    updateDF.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/newStringerDims.csv'), index=False)

    # # Cleanup data for output 
    # ## Drop unenessacry columns 
    lc1combined = lc1combined.drop(['Volume', 'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'VolumeTot'], axis=1)
    lc2combined = lc2combined.drop(['Volume', 'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'VolumeTot'], axis=1)
    lc3combined = lc3combined.drop(['Volume', 'tLeft', 'tRight', 'dim1', 'dim2', 'dim3', 'dim4', 'areaTot', 'VolumeTot'], axis=1)

    # ## ROUND & Add together the load cases
    # Rename colums for concat
    lc1combined = lc1combined.rename(columns={'sigma_XX_avg':'XX_avg_LC1', 'sigma_crit':'sigma_crit_LC1', 'Reserve Factor':'RF_LC1', 'sigma_crip':'sigma_crip_LC1'})
    lc2combined = lc2combined.rename(columns={'sigma_XX_avg':'XX_avg_LC2', 'sigma_crit':'sigma_crit_LC2', 'Reserve Factor':'RF_LC2', 'sigma_crip':'sigma_crip_LC2'})
    lc3combined = lc3combined.rename(columns={'sigma_XX_avg':'XX_avg_LC3', 'sigma_crit':'sigma_crit_LC3', 'Reserve Factor':'RF_LC3', 'sigma_crip':'sigma_crip_LC3'})

    outputdf = pd.concat([lc1combined,lc2combined,lc3combined], axis = 1)
    outputdf = outputdf.round(rounding_digits)
    # After concatenation, keep only the first column of cross section propertries and drop the rest
    outputdf['I_y'] = outputdf.filter(like='I_yy').iloc[:, 0]  # Take the first I_yy column
    outputdf['Lambda'] = outputdf.filter(like='lambda').iloc[:, 1]  # Take the first lambda column
    outputdf['Lambda_crit'] = outputdf.filter(like='lambda_crit').iloc[:, 0]  # Take the first I_yy column
    outputdf['R_gyr'] = outputdf.filter(like='r_gyr').iloc[:, 0]  # Take the first I_yy column
    outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('I_yy')])
    outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('lambda')])
    outputdf = outputdf.drop(columns=[col for col in outputdf.columns if col.startswith('r_gyr')])
    #outputdf.head(10)

    # # Generate output file
    outputdf.to_excel(os.path.join(BASE_DIR, f'../data/{name}/output/processed_f.xlsx'))

    #print("CS: Stringer calculations completed successfully.")

if __name__ == "__main__":
    calculate_stringers('yannis')