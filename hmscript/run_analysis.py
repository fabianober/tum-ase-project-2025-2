import hm
import os 

def run_run_analysis(name):
    input_strs_path = f"data/{name}/hmout/input.strs"
    if os.path.exists(input_strs_path):
        os.remove(input_strs_path)
    #Constants
    if name == 'felix':
        solver_template = "C:/Program Files/Altair/2024.1/hwdesktop/templates/feoutput/optistruct/optistruct"
    else:
        solver_template = "C:/Program Files/Altair/2025/hwdesktop/templates/feoutput/optistruct/optistruct"
    #print('RA: Running analysis for:', name)
    file_path = "data/"+ name +"/hmout/input.fem"
    solver_parameters = ["HM_NODEELEMS_SET_COMPRESS_SKIP ", "EXPORT_DMIG_LONGFORMAT ", "HMENGINEERING_XML", "HMSUBSYSTEMCOMMENTS_XML", "HMMATCOMMENTS_XML", "HMBOMCOMMENTS_XML", "INCLUDE_RELATIVE_PATH ", "EXPORT_SOLVER_DECK_XML_1 "]
    #Run analysis
    model = hm.Model()
    model.hm_answernext("yes") #overwrite file if necessary 
    model.feoutputwithdata(solver_template, file_path, 0,0,2, solver_parameters)
    #print('RA: We have created the .fem file for:', name)
    
    #print('RA: Running the solver now')
    if name == 'fabian':
        os.system(r'"C:\Program Files\Altair\2025\hwsolvers\scripts\optistruct.bat" data/fabian/hmout/input.fem')
    elif name == 'yannis':
        os.system(r'"C:\Program Files\Altair\2025\hwsolvers\scripts\optistruct.bat" data/yannis/hmout/input.fem')
    elif name == 'daniel':
        os.system(r'"C:\Program Files\Altair\2025\hwsolvers\scripts\optistruct.bat" data/daniel/hmout/input.fem')
    elif name == 'felix':
        #print("Bin da")
        os.system(r'"C:\Program Files\Altair\2024.1\hwsolvers\scripts\optistruct.bat" data/felix/hmout/input.fem')
    #else:
        ##print('RA: No valid name provided, cannot run solver')
    #print('RA: cleaning up the hmout folder')
    # remove all .out and .stat files
    for file in os.listdir(f"data/{name}/hmout"):
        if file.endswith(".out") or file.endswith(".stat"):
            os.remove(os.path.join(f"data/{name}/hmout", file))
    #print('RA: Analysis completed and cleaned up. YAY!')