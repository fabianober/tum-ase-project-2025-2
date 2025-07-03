import math

def constitutiveLawPlyProblemCOS(EModulus1, EModulus2, ShearModulus, mu12, theta):
    #Evaluating sinus and cosinus of theta
    sinus_theta = math.sin(math.radians(theta))
    cosinus_theta = math.cos(math.radians(theta))
    #Calculating constitutive law in material coordinate system
    mu21 = mu12*EModulus2/EModulus1
    q11 = EModulus1/(1-mu12*mu21)
    q12 = mu12*EModulus2/(1-mu12*mu21)
    q22 = EModulus2/(1-mu12*mu21)
    q66 = ShearModulus
    #Transform constitutive law to problem coordinate system
    q11_bar = q11*cosinus_theta**4 + 2*(q12 + 2*q66)*sinus_theta**2*cosinus_theta**2 + q22*sinus_theta**4
    q12_bar = (q11 + q22 - 4*q66)*sinus_theta**2*cosinus_theta**2 + q12*(sinus_theta**4 + cosinus_theta**4)
    q22_bar = q11*sinus_theta**4 + 2*(q12 + 2*q66)*sinus_theta**2*cosinus_theta**2
    q16_bar = (q11 - q12 - 2*q66)*sinus_theta*cosinus_theta**3 + (q12 - q22 + 2*q66)*sinus_theta**3*cosinus_theta
    q26_bar = (q11 - q12 - 2*q66)*cosinus_theta*sinus_theta**3 + (q12 - q22 + 2*q66)*cosinus_theta**3*sinus_theta
    q66_bar = (q11 + q22 - 2*q12 - 2*q66)*sinus_theta**2*cosinus_theta**2 + q66*(sinus_theta**4 + cosinus_theta**4)
    return q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar

