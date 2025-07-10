import math
import helpers as hp


def panel_element_volume(row, elementLength, elementWidth):
    panelVolume = (row['thickness']*elementLength*elementWidth)
    return panelVolume 

# dim1: flange width
# dim2: total height of T-Stringer (web+flange)
# dim3: flange thickness
# dim4: web thickness
# elementLength: length of the stringer element

def stringer_element_volume(row, elementLength):
    area_flange = row['dim3'] * row['dim1']
    area_web = row['dim4'] * (row['dim2'] - row['dim3'])
    areaTot = area_flange + area_web
    volume = areaTot * elementLength
    return volume

def crosssectional_properties_tee_skin(height_str, width_str, thickness_web, thickness_flange, thickness_skin_left,
                                       thickness_skin_right, stringer_pitch, E_x_skin, E_x_flange, E_x_web,
                                       E_y_skin, E_y_flange, E_y_web):

    # Individual moment of inertia calculations for the skin, flange, and web of a T-stringer
    I_y_skin_left = (stringer_pitch/2 * thickness_skin_left**3) / 12
    I_y_skin_right = (stringer_pitch/2 * thickness_skin_right**3) / 12
    I_y_flange = (width_str * thickness_flange**3) / 12
    I_y_web = (thickness_web*(height_str-thickness_flange)**3)/12

    # Calculate the centroid of the T-stringer
    z_skin_left = -thickness_skin_left / 2
    z_skin_right = -thickness_skin_left / 2 #Not an issue, as the skin is symmetric
    z_flange = thickness_flange/2
    z_web = thickness_flange + (height_str - thickness_flange) / 2

    # Calculate the area of each component
    A_skin_left = stringer_pitch/2 * thickness_skin_left
    A_skin_right = stringer_pitch/2 * thickness_skin_right
    A_flange = width_str * thickness_flange
    A_web = thickness_web * (height_str - thickness_flange)
    A_tot = A_skin_left + A_skin_right + A_flange + A_web

    # Elastic center calc 
    z_bar = (E_x_skin* A_skin_left * z_skin_left+ E_x_skin *A_skin_right*z_skin_right + 
            E_x_flange * A_flange * z_flange + E_x_web * A_web * z_web)/ (E_x_skin *A_skin_left + E_x_skin*A_skin_right+
                                                                          E_x_flange*A_flange +E_x_web*A_web )


    # combined moment of inertia
    contrib_skin_left = I_y_skin_left + (z_skin_left-z_bar)**2 * A_skin_left
    contrib_skin_right = I_y_skin_right + (z_skin_right-z_bar)**2 * A_skin_right
    contrib_flange = I_y_flange + (z_flange-z_bar)**2 * A_flange
    contrib_web = I_y_web + (z_web-z_bar)**2 * A_web
    I_y_bar = contrib_skin_left + contrib_skin_right + contrib_flange + contrib_web
    
    #Calculate the needed E_y_tot for the stability analysis 
    EI_comb = ((E_y_skin*I_y_skin_left+E_x_skin*A_skin_left*(z_skin_left-z_bar)**2) +
              (E_y_skin*I_y_skin_right+E_x_skin*A_skin_right*(z_skin_right-z_bar)**2)+
               (E_y_flange*I_y_flange+E_x_flange*A_flange*(z_flange-z_bar)**2)+
               (E_y_web*I_y_web+E_x_web*A_web*(z_web-z_bar)**2))
    E_y_tot = EI_comb/I_y_bar
    
    return I_y_bar, A_tot, EI_comb, E_y_tot, z_bar

# crosssectional_properties_tee_skin is an old function, which is not used anymore, but kept for reference.
def crosssectional_properties_hat_skin(DIM1, DIM2, DIM3, DIM4, thickness_skin_left,thickness_skin_right, stringer_pitch, stringer_depth):
    """
    DIM1: height of the hat section
    DIM2: thickness of hat elements
    DIM3: top horizontal part width
    DIM4: bottom flange width
    thickness_skin: thickness of skin
    stringer_pitch: width of skin area per stringer (used in skin calc)
    """

    # Area of each part
    A_skin_left = stringer_pitch/2 * thickness_skin_left
    A_skin_right = stringer_pitch/2 * thickness_skin_right
    A_top = DIM3 * DIM2
    A_side_web = DIM2 * (DIM1 - DIM2)
    A_bottom = DIM4 * DIM2
    A_tot = A_skin_left+ A_skin_right + A_top + 2 * A_side_web + 2 * A_bottom

    V_tot = A_tot * stringer_depth  # Volume of the entire cross-section

    # z-coordinates (from bottom)
    z_skin_left = -thickness_skin_left / 2
    z_skin_right = -thickness_skin_right / 2
    z_bottom = DIM2 / 2
    z_web = (DIM1 - DIM2) / 2 #+ DIM2
    z_top = DIM1 - DIM2 / 2

    # Centroid (z_bar)
    z_bar = (
        A_skin_left * z_skin_left +
        A_skin_right * z_skin_right+
        A_top * z_top +
        2 * A_side_web * z_web +
        2 * A_bottom * z_bottom
    ) / A_tot

    # Moment of inertia about y-axis for each component
    I_y_skin_left = (stringer_pitch/2 * thickness_skin_left**3) / 12
    I_y_skin_right = (stringer_pitch/2 * thickness_skin_right**3) / 12
    I_y_top = (DIM3 * DIM2**3) / 12
    I_y_webs = 2 * (DIM2 * (DIM1 - DIM2)**3) / 12
    I_y_bottoms = 2 * (DIM4 * DIM2**3) / 12

    # Parallel axis theorem
    contrib_skin_left = I_y_skin_left + A_skin_left * (z_skin_left - z_bar)**2
    contrib_skin_right = I_y_skin_right + A_skin_right * (z_skin_right - z_bar)**2
    contrib_top = I_y_top + A_top * (z_top - z_bar)**2
    contrib_webs = I_y_webs + 2 * A_side_web * (z_web - z_bar)**2
    contrib_bottoms = I_y_bottoms + 2 * A_bottom * (z_bottom - z_bar)**2 

    I_yy = contrib_skin_left + contrib_skin_right + contrib_top + contrib_webs + contrib_bottoms

    return I_yy, A_tot, V_tot  # Return moment of inertia, area, and volume

#Column Buckling formulas 
#Euler Buckling case 
def EulerBuckling(row, EModulus, c=1):
    lmd = row['lambda']
    sigma_crit = math.pi**2 * EModulus/(lmd**2)
    reserveFactor = sigma_crit/(1.5*row['sigma_XX_avg'])
    return sigma_crit, abs(reserveFactor)


#Euler Johnson with Crippling
def sigma_crip(sigma_u_c, DIM2, DIM3,DIM4, r):
    b = DIM2-DIM3
    sigma_crippling = sigma_u_c * 1.63/(b/DIM4)**0.717
    return sigma_crippling

def EulerJohnson(row, EModulus, c=1, r = 0):
    lmd = row['lambda']
    sigma_cripple = row['sigma_crip']    #returns the crippling stress of the hat-stringer
    sigma_crit = sigma_cripple - 1/EModulus*(sigma_cripple/(2*math.pi))**2 * lmd**2 # interpolate crictical stress
    reserveFactor = sigma_crit/(1.5*row['sigma_XX_avg'])
    return sigma_crit, abs(reserveFactor)

def chooseBuckling(row):
    if row['lambda'] > row['lambda_crit']:
        sigma_crit, reserveFactor = EulerBuckling(row, EModulus=row['E_y_comb'])
    elif row['lambda'] <= row['lambda_crit']:
        sigma_crit, reserveFactor = EulerJohnson(row, EModulus=row['E_y_comb'])
    return sigma_crit, reserveFactor


#Ramberg Osgood
"""
Ramberg-Osgood function is not functional at the moment!
"""
def RambergOsgoodIt(EModulus, I_y, area, length, sigma_applied, sigma_02, sigma_u, epsilon_u, c=1, tol=0.001):
    lmd = hp.lmd(I_y, area, length, c)
    n = math.log(epsilon_u / 0.002) / math.log(sigma_u / sigma_02) # exponent

    # Start from the applied stress (initial)
    sigma_crit = sigma_applied
    step = 0.2  # Initial step size
    direction = -1  # 1 for increasing, -1 for decreasing (This is arbitrary tbh)

    while True:
        # Compute tangent modulus at current stress
        denom = 1 + 0.002 * n * (EModulus / sigma_02) * ((sigma_crit / sigma_02) ** (n - 1))
        Et = EModulus / denom

        # Compute critical stress from updated tangent modulus
        sigma_new = (math.pi**2 * Et) / (lmd**2)

        diff = sigma_new - sigma_crit

        # For overshot, reverse direction *-1 and reduce step size by 50%
        if direction * diff < 0:
            step *= 0.5
            direction *= -1

        # Update sigma_crit
        sigma_crit = sigma_crit + direction * step * abs(diff)

        # Break out, if diff between sigma_new and sigma_crit is smaller than tol=0.01
        if abs(diff) < tol:
            break

    reserveFactor = sigma_crit / sigma_applied
    return sigma_crit, reserveFactor #return(critical stress, reserve factor)

#Test cases for the formula 
if __name__ == '__main__':
    # Example usage of crosssectional_properties_hat_skin
    crossecProp = crosssectional_properties_hat_skin(DIM1=25, DIM2=2, DIM3=20, DIM4=15, thickness_skin=4, stringer_pitch=200, stringer_depth=750/3)
    print(f"Area: {crossecProp[1]}, Moment of Inertia: {crossecProp[0]}, Volume: {crossecProp[2]}")

    # Example usage of RambergOsgoodIt
    res = RambergOsgoodIt(EModulus=72000, I_y=crossecProp[1], area=crossecProp[0], length=600, sigma_applied=200, sigma_02=280, sigma_u=350, epsilon_u=0.1)
    # we expect arround: Et=64605, sigma_crit=218.9, reserveFactor=0.78
    print(res)

    #Example for Euler Crippling 
    #sigma_crit, reserveFactor = EulerJohnson(EModulus=72000, I_y = 79820.4, area=646, length=600, height_str=45, thickness_flange=3, thickness_web=3, radius = 2, sigma_yield=280, sigma_applied=200)
    #sigma_crit_expect = 131.65
    #reserveFactor_expect = 0.66
    #print('The resulting crictical stress is: '+str(sigma_crit)+' And the corresponding reserve Factor: '+ str(reserveFactor))
    #print('The test status is thus: '+str(sigma_crit==sigma_crit_expect and reserveFactor==reserveFactor_expect))

    #res3 = crosssectional_properties_hat_skin(10, 10, 10, 10, 10, 10)
    #print(f"Hat Section Area: {res3[0]}, Moment of Inertia: {res3[1]}")