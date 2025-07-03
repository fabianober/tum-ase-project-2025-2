# # Calculating the reserve Factors of the panels 

# # Imports 

import pandas as pd
import sys 
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, '..')))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, '../formulas')))
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, '../optimization')))

from formulas.panels import *
from formulas.helpers import *
from optimization.panelBuckReverse import *
from optimization.generation import *
 
rounding_digits = 3

def calculate_panels(name, RFgoal=1):
    # # Constants (Changed based on your data)
    personal_data = personal_data_provider(name)
    sigma_yield = personal_data[0]
    EModulus = personal_data[1]
    nu = personal_data[2]
    #print(f"CP: Your personal data is: sigma_yield = {sigma_yield}, EModulus = {EModulus}, nu = {nu}. Please verify!")

    #Panel constants 
    length = 750
    width = 200


    # # Open stress values & properties of panels 

    # New version of importing panel stress file
    paneldf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/panel.csv'))

    #Import panel properties and reformat
    panelPropertiesdf = pd.read_csv(os.path.join(BASE_DIR, f'../data/{name}/properties/panel_properties.csv'), index_col=0)
    panelPropertiesdf = panelPropertiesdf.reset_index()
    panelPropertiesdf = panelPropertiesdf.drop(columns=['Component Name', 'mass'])

    # # Split up the loadcases 


    loadCase1df = paneldf[paneldf['Load Case'] == 'Subcase 1 (LC1)']
    loadCase2df = paneldf[paneldf['Load Case'] == 'Subcase 2 (LC2)']
    loadCase3df = paneldf[paneldf['Load Case'] == 'Subcase 3 (LC3)']
    # Add the data to load case 
    loadCase1df = pd.merge(loadCase1df, panelPropertiesdf, on='Element ID')
    loadCase2df = pd.merge(loadCase2df, panelPropertiesdf, on='Element ID')
    loadCase3df = pd.merge(loadCase3df, panelPropertiesdf, on='Element ID')

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
        'thickness':'max'
    })
    dataframeLength = len(panelLC1)
    panelLC1['length'] = [length]*dataframeLength
    panelLC1['width'] = [width]*dataframeLength
    panelLC1['Load Case'] = ['LC1'] * dataframeLength


    #For load case 2 
    panelLC2 = loadCase2df.groupby('Component Name').agg({
        'sigmaXX': 'mean',
        'sigmaYY':'mean',
        'sigmaXY':'mean',
        'thickness':'max'
    })
    dataframeLength = len(panelLC2)
    panelLC2['length'] = [length]*dataframeLength
    panelLC2['width'] = [width]*dataframeLength
    panelLC2['Load Case'] = ['LC2'] * dataframeLength


    #For load case 3
    panelLC3 = loadCase3df.groupby('Component Name').agg({
        'sigmaXX': 'mean',
        'sigmaYY':'mean',
        'sigmaXY':'mean',
        'thickness':'max'
    })
    dataframeLength = len(panelLC3)
    panelLC3['length'] = [length]*dataframeLength
    panelLC3['width'] = [width]*dataframeLength
    panelLC3['Load Case'] = ['LC3'] * dataframeLength


    # # Now we can apply the functions to the load cases 


    panelLC1[['k_shear', 'k_biaxial', 'Reserve Factor']] = panelLC1.apply(panelBuckApply, EModulus=EModulus, nu=nu, axis=1, result_type='expand')
    panelLC2[['k_shear', 'k_biaxial', 'Reserve Factor']] = panelLC2.apply(panelBuckApply, EModulus=EModulus, nu=nu, axis=1, result_type='expand')
    panelLC3[['k_shear', 'k_biaxial', 'Reserve Factor']] = panelLC3.apply(panelBuckApply, EModulus=EModulus, nu=nu, axis=1, result_type='expand')


    # # Combining back into 1 Data Frame for updating thickness

    updateParametersDf = pd.concat([panelLC1, panelLC2, panelLC3], axis=0)
    updateParametersDf = updateParametersDf.reset_index()
    evaluateDf = updateParametersDf.copy()


    # ## Now we have to apply our reverse engineering and compute the thicknesses

    updateParametersDf["thickness"] = updateParametersDf.apply(panelBuckReverse,EModulus=EModulus, nu=nu,RF_goal=RFgoal, axis=1)


    #Drop irrelevant columns
    updateParametersDf = updateParametersDf.drop(['length', 'width'], axis=1)


    updateParametersDf = updateParametersDf.groupby('Component Name').agg({
        'thickness':'max'
    })


    # # Score the corresponding parameter set 


    evaluateDf = evaluateDf.drop(['sigmaXX', 'sigmaYY', 'sigmaXY', 'length', 'width', 'k_shear', 'k_biaxial'], axis =1)

    evaluateDf.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/PanelRFs.csv'), index=False)

    evaluateDf['score'] = evaluateDf.apply(rf_score, axis=1)


    # ## Extract score and parameters

    score = evaluateDf['score'].sum()
    thicknesses = extractThickness(evaluateDf)

    evaluateDf = pd.DataFrame({
        'panel thickness': [thicknesses],
        'score': [score],
        'minRF':[evaluateDf['Reserve Factor'].min()]
    })


    # ## Save score file

    #evaluateDf = evaluateDf.round(rounding_digits)
    evaluateDf.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/panelScore.csv'), index=False)


    # # Create original output


    #Drop irrelevant columns
    panelLC1 = panelLC1.drop(['length','thickness', 'width', 'Load Case'], axis=1)
    panelLC2 = panelLC2.drop(['length','thickness', 'width',  'Load Case'], axis=1)
    panelLC3 = panelLC3.drop(['length','thickness', 'width',  'Load Case'], axis=1)


    # Rename columns to be unambigous
    panelLC1 = panelLC1.rename(columns={"Reserve Factor": "LC 1 RF", 'sigmaXX':'sigmaXXLC1', 'sigmaYY':'sigmaYYLC1', 'sigmaXY':'sigmaXYLC1', 'k_shear':'k_shearLC1', 'k_biaxial':'k_biaxialLC1'})
    panelLC2 = panelLC2.rename(columns={"Reserve Factor": "LC 2 RF", 'sigmaXX':'sigmaXXLC2', 'sigmaYY':'sigmaYYLC2', 'sigmaXY':'sigmaXYLC2', 'k_shear':'k_shearLC2', 'k_biaxial':'k_biaxialLC2'})
    panelLC3 = panelLC3.rename(columns={"Reserve Factor": "LC 3 RF", 'sigmaXX':'sigmaXXLC3', 'sigmaYY':'sigmaYYLC3', 'sigmaXY':'sigmaXYLC3', 'k_shear':'k_shearLC3', 'k_biaxial':'k_biaxialLC3'})


    outputDf = pd.concat([panelLC1, panelLC2, panelLC3], axis=1)


    # # ROUND & Output the files

    #outputDf = outputDf.round(rounding_digits)
    outputDf.to_excel(os.path.join(BASE_DIR, f'../data/{name}/output/processed_e.xlsx'))
    updateParametersDf = updateParametersDf.round(rounding_digits)
    updateParametersDf.to_csv(os.path.join(BASE_DIR, f'../data/{name}/output/updatePanelThick.csv'))

    #print(f"CP: Successfully calculated panels for {name} and saved the results to the data folder.")

if __name__ == "__main__":
    calculate_panels('fabian')