import math
import helpers as hp


def panel_element_volume(row, elementLength, elementWidth):
    halfVolume = (row['thickness']*elementLength*elementWidth)/2
    return halfVolume 

def stringer_element_volume(row, elementLength):
    area_top = row['dim3'] * row['dim2']
    area_side_web = row['dim2'] * (row['dim1'] - row['dim2'])
    area_bottom = row['dim4'] * row['dim2']
    areaTot = area_top + 2 * area_side_web + 2 * area_bottom
    volume = areaTot * elementLength
    return volume

def crosssectional_properties_tee_skin(height_str, width_str, thickness_web, thickness_flange, thickness_skin, stringer_pitch):

    # Individual moment of inertia calculations for the skin, flange, and web of a T-stringer
    I_y_skin = (stringer_pitch * thickness_skin**3) / 12
    I_y_flange = (width_str * thickness_flange**3) / 12
    I_y_web = (thickness_web*(height_str-thickness_web)**3)/12

    # Calculate the centroid of the T-stringer
    z_skin = -thickness_skin / 2
    z_flange = thickness_flange/2
    z_web = thickness_flange + (height_str - thickness_flange) / 2

    # Calculate the area of each component
    A_skin = stringer_pitch * thickness_skin
    A_flange = width_str * thickness_flange
    A_web = thickness_web * (height_str - thickness_flange)
    A_tot = A_skin + A_flange + A_web

    z_bar = (A_skin * z_skin + A_flange * z_flange + A_web * z_web) / A_tot


    # combined moment of inertia
    contrib_skin = I_y_skin + (z_skin-z_bar)**2 * A_skin
    contrib_flange = I_y_flange + (z_flange-z_bar)**2 * A_flange
    contrib_web = I_y_web + (z_web-z_bar)**2 * A_web
    I_y_bar = contrib_skin + contrib_flange + contrib_web

    return A_tot, I_y_bar

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
def sigma_crip(EModulus, DIM1, DIM2, DIM3, sigma_yield, r):
    #We have a HAT-Stringer attached to the skin
    #Support factor for relevant parts of stringer
    ki1 = 3.6
    ki2 = 0
    if DIM1 - DIM2 > 0.2*DIM3:
       ki2 = 3.6
    else:
       ki2 = 0.41
    #Effective width of crippling-affected parts of the HAT-stringer 
    b1 = DIM1 - DIM2*(1 - 0.2*(r**2/DIM2**2))
    b2 = DIM3 - DIM2*(1 - 0.2*(r**2/DIM2**2))
    #slenderness of the crippling-affected parts of the HAT-stringer
    x1 = b1/DIM2 * math.sqrt(sigma_yield/(ki1*EModulus))
    x2 = b2/DIM2 * math.sqrt(sigma_yield/(ki2*EModulus))
    #Compute the scaling factors alpha 1 & alpha 2
    alpha1 = 0
    if 0.4 <= x1 <= 1.095:
        alpha1 = 1.4-0.628*x1
    elif 1.095 < x1 <=1.633:
        alpha1 = 0.78/x1
    elif 1.633 < x1:
        alpha1 = 0.69/ pow(x1,0.75)
    alpha2 = 0
    if 0.4 <= x2 <= 1.095:
        alpha2 = 1.4-0.628*x2
    elif 1.095 < x2 <=1.633:
        alpha2 = 0.78/x2
    elif 1.633 < x2:
        alpha2 = 0.69/ pow(x2,0.75)

    sigma_crippling1 = alpha1 * sigma_yield   #Compute crippling stress 1
    sigma_crippling2 = alpha2 * sigma_yield   #Compute crippling stress 2
    #Check weather one of the components cannot cripple at all ie xi<0.4
    # Both components can cripple 
    if alpha1 != 0 and alpha2!= 0:
        sigma_crippling = (2*sigma_crippling1*b1 + sigma_crippling2*b2)/(2*b1 + b2)
    # Only component 1 can cripple 
    elif alpha2 == 0 and alpha1 != 0:
        sigma_crippling = sigma_crippling1
    # Only component 2 can cripple 
    elif alpha1 == 0 and alpha2 != 0:
        sigma_crippling = sigma_crippling2
    # If both cannot cripple 
    else:
        sigma_crippling = sigma_yield
    sigma_crippling = min(sigma_crippling,sigma_yield)
    return sigma_crippling

def EulerJohnson(row, EModulus, sigma_yield, c=1, r = 0):
    lmd = row['lambda']
    sigma_cripple = row['sigma_crip']    #returns the crippling stress of the hat-stringer
    sigma_cutoff = min(sigma_cripple, sigma_yield)  #Determine the inzterpolation stress
    sigma_crit = sigma_cutoff - 1/EModulus*(sigma_cutoff/(2*math.pi))**2 * lmd**2 # interpolate crictical stress
    reserveFactor = sigma_crit/(1.5*row['sigma_XX_avg'])
    return sigma_crit, abs(reserveFactor)

def chooseBuckling(row, EModulus, sigma_yield):
    if row['lambda'] > row['lambda_crit']:
        sigma_crit, reserveFactor = EulerBuckling(row, EModulus=EModulus)
    elif row['lambda'] <= row['lambda_crit']:
        sigma_crit, reserveFactor = EulerJohnson(row, EModulus=EModulus, sigma_yield=sigma_yield)
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