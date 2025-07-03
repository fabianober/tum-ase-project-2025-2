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

def aMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_bottom, z_top):
    for j in range(0,k):
        a11 += q11_bar[j]*(z_top[j] - z_bottom[j])
        a12 += q12_bar[j]*(z_top[j] - z_bottom[j])
        a22 += q22_bar[j]*(z_top[j] - z_bottom[j])
        a16 += q16_bar[j]*(z_top[j] - z_bottom[j])
        a26 += q26_bar[j]*(z_top[j] - z_bottom[j])
        a66 += q66_bar[j]*(z_top[j] - z_bottom[j])
    return a11, a12, a22, a16, a26, a66

def bMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_bottom, z_top):
    for j in range(0,k):
        b11 += 0.5*q11_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
        b12 += 0.5*q12_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
        b22 += 0.5*q22_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
        b16 += 0.5*q16_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
        b26 += 0.5*q26_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
        b66 += 0.5*q66_bar[j]*(z_top[j]**2 - z_bottom[j]**2)
    return b11, b12, b22, b16, b26, b66

def dMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_bottom, z_top):
    for j in range(0,k):
        d11 += (1/3)*q11_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
        d12 += (1/3)*q12_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
        d22 += (1/3)*q22_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
        d16 += (1/3)*q16_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
        d26 += (1/3)*q26_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
        d66 += (1/3)*q66_bar[j]*(z_top[j]**3 - z_bottom[j]**3)
    return d11, d12, d22, d16, d26, d66