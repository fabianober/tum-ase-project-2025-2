import math
import columnbuckling as colbuckl

def lmd(I_y, area, length, c=1):
    r = math.sqrt(I_y/area) 
    lmd = (c*length)/r
    return lmd

def lambda_crit(EModulus, sigma_crip):
    sigma_cutoff = sigma_crip
    return math.sqrt(2*(math.pi**2) * EModulus / sigma_cutoff)

def r_gyr(I_y, area):
    return math.sqrt(I_y / area)

def crosssectional_properties_tee_skin_row(row, stringer_pitch, E_y_skin, E_y_flange, E_y_web, E_x_skin, E_x_flange, E_x_web):
    return colbuckl.crosssectional_properties_tee_skin(
        height_str=row['dim2'],
        width_str=row['dim1'],
        thickness_web=row['dim4'],
        thickness_flange=row['dim3'],
        thickness_skin_left=row['tLeft'],
        thickness_skin_right=row['tRight'],
        stringer_pitch=stringer_pitch,
        E_x_skin = E_x_skin,
        E_x_flange = E_x_flange,
        E_x_web = E_x_web,
        E_y_skin = E_y_skin,
        E_y_flange =  E_y_flange,
        E_y_web = E_y_web 
    )

def crosssectional_properties_hat_skin_row(row, stringer_pitch, stringer_depth):
    return colbuckl.crosssectional_properties_hat_skin(
        DIM1=row['dim1'],
        DIM2=row['dim2'],
        DIM3=row['dim3'],
        DIM4=row['dim4'],
        thickness_skin_left=row['tLeft'],
        thickness_skin_right=row['tRight'],
        stringer_pitch=stringer_pitch,
        stringer_depth=stringer_depth,
       
    )



def personal_data_provider(name):
    if name == 'yannis':
        EModulus11 = 132583.92 
        EModulus22 = 10198.76 
        G12 = 5099.38 
        nu12 = 0.33
    elif name == 'fabian':
        sigma_yield = 490
        EModulus = 65420.46
        nu = 0.34
        max_mass = 28.667
    elif name == 'daniel':
        sigma_yield = 490
        EModulus = 65669.47
        nu = 0.34
        max_mass = 28.821
    elif name == 'felix':
        sigma_yield = 490
        EModulus = 65143.57
        nu = 0.34
        max_mass = 28.667 # PLEASE CHANGE!
    return EModulus11, EModulus22, G12, nu12

def elementComponentMatch(row):
    # Here we write some ugly code to match the elements with their components
    # Panel component matching 
    panel1IDs = [1,2,3,4,5,6]
    panel2IDs = [7,8,9,10,11,12]
    panel3IDs = [13,14,15,16,17,18]
    panel4IDs = [19,20,21,22,23,24]
    panel5IDs = [25,26,27,28,29,30]

    #Stringer component matching 
    stringer1IDs = [40,41,42]
    stringer2IDs = [46,47,48]
    stringer3IDs = [52,53,54]
    stringer4IDs = [58,59,60]
    
    CompName = None
    #Matching panels
    if row['Element ID'] in panel1IDs:
        CompName = 'panel1'
    elif row['Element ID'] in panel2IDs:
        CompName = 'panel2'
    elif row['Element ID'] in panel3IDs:
        CompName = 'panel3'
    elif row['Element ID'] in panel4IDs:
        CompName = 'panel4'
    elif row['Element ID'] in panel5IDs:
        CompName = 'panel5'

    #Matching stringers 
    elif row['Element ID'] in stringer1IDs:
        CompName = 'stringer1'
    elif row['Element ID'] in stringer2IDs:
        CompName = 'stringer2'
    elif row['Element ID'] in stringer3IDs:
        CompName = 'stringer3'
    elif row['Element ID'] in stringer4IDs:
        CompName = 'stringer4'
    return CompName

#Running test on all functions 
if __name__ == '__main__':
    print(lmd(I_y=79820.37, area=646, length=600, c=1), "and expected: 53.97")