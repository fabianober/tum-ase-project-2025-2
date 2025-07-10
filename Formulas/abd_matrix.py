import math
import numpy as np 
def constitutiveLawPlyProblemCOS(EModulus1, EModulus2, ShearModulus, theta, mu12=0.33):
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
    q22_bar = q11*sinus_theta**4 + 2*(q12 + 2*q66)*sinus_theta**2*cosinus_theta**2 + q22 * cosinus_theta**4
    q16_bar = (q11 - q12 - 2*q66)*sinus_theta*cosinus_theta**3 + (q12 - q22 + 2*q66)*sinus_theta**3*cosinus_theta
    q26_bar = (q11 - q12 - 2*q66)*cosinus_theta*sinus_theta**3 + (q12 - q22 + 2*q66)*cosinus_theta**3*sinus_theta
    q66_bar = (q11 + q22 - 2*q12 - 2*q66)*sinus_theta**2*cosinus_theta**2 + q66*(sinus_theta**4 + cosinus_theta**4)
    return [q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar]

def aMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_cords):
    a11 = 0 
    a12 = 0
    a22 = 0
    a16 = 0
    a26 = 0
    a66 = 0
    for j in range(0,k):
        a11 += q11_bar[j]*(z_cords[j+1] - z_cords[j])
        a12 += q12_bar[j]*(z_cords[j+1] - z_cords[j])
        a22 += q22_bar[j]*(z_cords[j+1] - z_cords[j])
        a16 += q16_bar[j]*(z_cords[j+1] - z_cords[j])
        a26 += q26_bar[j]*(z_cords[j+1] - z_cords[j])
        a66 += q66_bar[j]*(z_cords[j+1] - z_cords[j])
    return [a11, a12, a22, a16, a26, a66]

def bMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_cords):
    b11 = 0 
    b12 = 0
    b22 = 0
    b16 = 0
    b26 = 0
    b66 = 0
    for j in range(0,k):
        b11 += 0.5*q11_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
        b12 += 0.5*q12_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
        b22 += 0.5*q22_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
        b16 += 0.5*q16_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
        b26 += 0.5*q26_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
        b66 += 0.5*q66_bar[j]*(z_cords[j+1]**2 - z_cords[j]**2)
    return [b11, b12, b22, b16, b26, b66]

def dMatrix (k, q11_bar, q12_bar, q22_bar, q16_bar, q26_bar, q66_bar, z_cords):
    d11 = 0 
    d12 = 0
    d22 = 0
    d16 = 0
    d26 = 0
    d66 = 0
    for j in range(0,k):
        d11 += (1/3)*q11_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
        d12 += (1/3)*q12_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
        d22 += (1/3)*q22_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
        d16 += (1/3)*q16_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
        d26 += (1/3)*q26_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
        d66 += (1/3)*q66_bar[j]*(z_cords[j+1]**3 - z_cords[j]**3)
    return [d11, d12, d22, d16, d26, d66]

def calculateABD(stacksequence, plyT, EModulus1, EModulus2, ShearModulus):
    numberOfPlies = len(stacksequence)
    #Calculate the z coordinates of the laminate  
    zcords=[]
    for i in range(int(numberOfPlies/2),-1,-1):
        zcords.append(-i*plyT)
    for i in range(1,int((numberOfPlies/2)+1)):
        zcords.append(i*plyT)
    #Calculate Q_bar for each ply and safe it in array 
    q_11_bar = []
    q_12_bar = []
    q_22_bar = []
    q_16_bar = []
    q_26_bar = []
    q_66_bar = []

    for i in range(0,numberOfPlies):
        q_bar = constitutiveLawPlyProblemCOS(EModulus1=EModulus1, EModulus2=EModulus2,ShearModulus=ShearModulus, theta=stacksequence[i])
        q_11_bar.append(q_bar[0])
        q_12_bar.append(q_bar[1])
        q_22_bar.append(q_bar[2])
        q_16_bar.append(q_bar[3])
        q_26_bar.append(q_bar[4])
        q_66_bar.append(q_bar[5])

    #Calculate the A, B and D matrices 
    AMatrix = aMatrix(k=numberOfPlies, q11_bar= q_11_bar, q12_bar=q_12_bar, q22_bar=q_22_bar, q16_bar=q_16_bar, q26_bar=q_26_bar, q66_bar=q_66_bar, z_cords=zcords)
    BMatrix = bMatrix(k=numberOfPlies, q11_bar= q_11_bar, q12_bar=q_12_bar, q22_bar=q_22_bar, q16_bar=q_16_bar, q26_bar=q_26_bar, q66_bar=q_66_bar, z_cords=zcords)
    DMatrix = dMatrix(k=numberOfPlies, q11_bar= q_11_bar, q12_bar=q_12_bar, q22_bar=q_22_bar, q16_bar=q_16_bar, q26_bar=q_26_bar, q66_bar=q_66_bar, z_cords=zcords)
    
    #Assemble to ABD matrix 
    ABD = np.array([[AMatrix[0], AMatrix[1], AMatrix[3], BMatrix[0], BMatrix[1], BMatrix[3]],
                    [AMatrix[1], AMatrix[2], AMatrix[4], BMatrix[1], BMatrix[2], BMatrix[4]],
                    [AMatrix[3], AMatrix[4], AMatrix[5], BMatrix[3], BMatrix[4], BMatrix[5]],
                    [BMatrix[0], BMatrix[1], BMatrix[3], DMatrix[0], DMatrix[1], DMatrix[3]],
                    [BMatrix[1], BMatrix[2], BMatrix[4], DMatrix[1], DMatrix[2], DMatrix[4]],
                    [BMatrix[3], BMatrix[4], BMatrix[5], DMatrix[3], DMatrix[4], DMatrix[5]]])
    
    #Compute the inverse 
    ABD_inverse = np.linalg.inv(ABD)
    return np.round(ABD, decimals=10), np.round(ABD_inverse, decimals=10)


if __name__=='__main__':
    ABD, ABD_inverse = calculateABD([0,90,90,0], 0.2)

def tSigmaMatrix(theta):
    #Evaluating sinus and cosinus of theta
    sinus_theta = math.sin(math.radians(theta))
    cosinus_theta = math.cos(math.radians(theta))
    #Determine entries of the T-sigma-matrix
    t11 = cosinus_theta**2
    t12 = sinus_theta**2
    t13 = 2*sinus_theta*cosinus_theta
    t23 = -2*sinus_theta*cosinus_theta
    t31 = -sinus_theta*cosinus_theta
    t33 = cosinus_theta**2 - sinus_theta**2
    #Assemble T-sigma-matrix
    tSigma = np.array([[t11, t12, t13],
                       [t12, t11, t23],
                       [t31, -t31, t33]])
    return tSigma