import sys
import os
import importlib.util

sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('hmscript'))
sys.path.insert(0, os.path.abspath('formulas'))
sys.path.insert(0, os.path.abspath('calculators'))

from abd_matrix import *
from helpers import *
import pandas as pd

with open("./name.txt", "r") as f:
    name = f.read().strip()

personal_data = personal_data_provider(name)
E_11_avg = personal_data[0]
E_22_avg = personal_data[1]
G_12_avg = personal_data[2]

print("Starting analysis...")
print(f"Your data is: Name: {name}, E_11_avg: {E_11_avg}, E_22_avg: {E_22_avg}, G_12_avg: {G_12_avg}")

#'Start by defining some of the necessary dimensions'
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

print("\n ABD matrix for panel: \n")
print_ABD_matrix(np, ABD_panel)
print("\n\n Inverse ABD matrix for panel: \n")
print(ABD_panel_inverse)


# Save ABD_panel to Excel
abd_panel_df = pd.DataFrame(ABD_panel)
abd_panel_df.to_excel(f"data/{name}/output/ABD_panel.xlsx", index=False, header=False)
print(f"\nABD_panel matrix has been saved to 'data/{name}/output/ABD_panel.xlsx'.")


# Calculate the homogonized average axial EModulus 
E_avg_x_web = 1/(ABD_web_inverse[0][0]*4)
A_web = 40*4
E_avg_x_flange = ABD_flange[0][0]/4
A_flange = 70*4
E_avg_x = (E_avg_x_web*A_web + E_avg_x_flange*A_flange)/(A_web+A_flange)
print('\n\n Your homogonized average Ex is: '+str(E_avg_x))


print("\nWe will now run task 1f\n")
# Dynamically import the 'task_1f' module from the 'calculators' directory
task_1f_path = os.path.join('calculators', 'task_1f.py')  # Build the path to the module
spec = importlib.util.spec_from_file_location("task_1f", task_1f_path)  # Create a module spec
task_1f = importlib.util.module_from_spec(spec)  # Create a module object from the spec
spec.loader.exec_module(task_1f)  # Load and execute the module

print("\n We will now run task 1e\n")
# Dynamically import the 'task_1e' module from the 'calculators' directory
task_1e_path = os.path.join('calculators', 'task_1e.py')  # Build the path to the module
spec = importlib.util.spec_from_file_location("task_1e", task_1e_path)  # Create a module spec
task_1e = importlib.util.module_from_spec(spec)  # Create a module object from the spec
spec.loader.exec_module(task_1e)  # Load and execute the module

print("\n We will now run the strength analysis\n")
# Dynamically import the 'task_1e' module from the 'calculators' directory
strength_analysis_path = os.path.join('calculators', 'strength_analysis.py')  # Build the path to the module
spec = importlib.util.spec_from_file_location("strength_analysis", strength_analysis_path)  # Create a module spec
strength_analysis = importlib.util.module_from_spec(spec)  # Create a module object from the spec
spec.loader.exec_module(strength_analysis)  # Load and execute the module