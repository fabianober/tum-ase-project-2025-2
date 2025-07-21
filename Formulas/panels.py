import math
import numpy as np 

#Define variables to check range of half waves 
N = 10
M = 20


def biaxialSS_calc(D11, D12, D22, D66, length, width, thickness, sigma_x, sigma_y):
    global N 
    global M
    #Control if panel needs to be flipped
    if sigma_y < sigma_x: 
        #Swap stresses 
        sigma_temp = sigma_x
        sigma_x = sigma_y
        sigma_y = sigma_temp
        #swap dimensions
        length_temp = length
        length = width
        width = length_temp
        #Swap D entries 
        D11_temp = D11
        D11 = D22
        D22 = D11_temp 


    sigma_crit_it = dict()  #Create dictionary to store the critcial stresses for different n,m
    alpha = length/width
    beta = sigma_y/sigma_x
    
    #Looping over n half waves in width direction and over m half waves in length direction 
    for n in range(1,N):        
        for m in range(1,M):
            sigma_crit = math.pi**2/(width**2 * thickness) * 1/((m/alpha)**2 + beta*n**2) * (D11 * (m/alpha)**4 + 2*(D12+D66) * ((m*n)/alpha)**2 + D22 * n**4) #Here was a plus and not a times 
            if sigma_crit> 0:
                sigma_crit_it.update({(n,m):sigma_crit})                                    #critical stress dictionary in dependence of m and n 
    finalN, finalM = min(sigma_crit_it, key = sigma_crit_it.get)    #Select the smallest critcial stress and recover n and m 
    sigma_crit_min = sigma_crit_it[(finalN,finalM)] 
    reserveFactor = sigma_crit_min / (sigma_x*1.5)                          #Calculate the reserve factor based on this the critical stress, 1.5 to get ultimate loads for the reserve factor
    return finalN, finalM, sigma_crit_min, abs(reserveFactor)

def shearSS_calc(D11, D12 , D22, D66 , length, width, thickness, tau_xy):
    delta = math.sqrt(D11*D22)/(D12+2*D66)
    if delta < 1:
        tau_crit = 4/(thickness*width**2) *(math.sqrt(D22*(D12+2*D66)) * (11.7+0.532*delta+0.938*delta**2))
    elif delta >= 1:
        tau_crit = 4/(thickness*width**2) * ((D11*D22**3)**(1/4) * (8.12 + 5.05/delta))
    
    reserveFactor = tau_crit / (tau_xy*1.5) # 1.5 to get ultimate loads for the reserve factor
    return tau_crit, abs(reserveFactor)


def combinedBiaxialShear(D11, D12, D22, D66, length, width, thickness, sigma_x, sigma_y, tau_xy):
    finalN, finalM, sigma_crit_biaxial, reserveFactorBi = biaxialSS_calc(D11=D11, D12=D12, D22=D22, D66=D66, length=length, width=width, thickness=thickness, sigma_x= sigma_x, sigma_y=sigma_y)
    tau_crit, reserveFactorShear = shearSS_calc(D11=D11, D12=D12, D22=D22, D66=D66, length=length, width=width, thickness=thickness, tau_xy=tau_xy)
    combinedReserveFactor = 1/(1/reserveFactorBi + pow(1/reserveFactorShear,2))
    return tau_crit, sigma_crit_biaxial, abs(combinedReserveFactor)


# Function for calling other buckling formulas with row values 
def panelBuckApply(row, D11, D12, D22, D66):
    tau_crit, sigma_crit_bi, reserveFactor = combinedBiaxialShear(D11=D11, D12=D12, D22=D22, D66=D66, length=row['length'], width=row['width'], thickness=row['thickness'], sigma_x=row['sigmaXX'], sigma_y=row['sigmaYY'], tau_xy=row['sigmaXY'] )
    return tau_crit, sigma_crit_bi, reserveFactor 

















#Running test on all functions 
if __name__ == '__main__':
    # Define test data
    E = 70000
    nu = 0.3
    length = 600
    width = 200
    thickness = 5
    sigma_x = -100
    sigma_y = -20
    tau_xy = 75
    # Expected results 
    # Biaxial calculation
    finalN_bi_expect = 1 
    finalM_bi_expect = 2
    sigma_crit_bi_expect = 128.02
    biReserveFactor_expect = 1.28

    #Shear calculation 
    tau_crit_expect = 228.73
    shearReserveFactor_expect = 3.05

    # Combined shear and biaxial calculation 
    combinedReserveFactor_expect = 1.13

    # Run tests
    #uniaxialF_calc()
    #uniaxialSS_calc()
    finalN_bi, finalM_bi, sigma_crit_bi, biReserveFactor = biaxialSS_calc(EModulus=E, nu=nu, length=length, width=width, thickness=thickness, sigma_x=sigma_x, sigma_y= sigma_y)
    tau_crit, shearReserveFactor = shearSS_calc(EModulus=E, nu=nu, length=length, width= width, thickness=thickness, tau_xy=tau_xy ) 
    combinedReserveFactor = combinedBiaxialShear(EModulus=E, nu=nu, length=length, width=width, thickness=thickness, sigma_x=sigma_x, sigma_y= sigma_y, tau_xy=tau_xy)
    # Output test results
    #Biaxial test
    print('The biaxial test resulted in the following values')
    print('Number of halfwaves in width direction: '+str(finalN_bi))
    print('Number of halfwaves in longitudinal direction: '+str(finalM_bi))
    print('A critical stress of: '+str(sigma_crit_bi)+' And a reserve factor of: '+str(biReserveFactor))
    print('The test comes out to be: '+ str(finalN_bi==finalN_bi_expect and finalM_bi==finalM_bi_expect and sigma_crit_bi==sigma_crit_bi_expect and biReserveFactor==biReserveFactor_expect))
    print()
    #Shear test
    print('The shear test resulted in the following values')
    print('A critical stress of: '+str(tau_crit)+' And a reserve factor of: '+str(shearReserveFactor))
    print('The test comes out to be: '+str(shearReserveFactor==shearReserveFactor_expect and tau_crit==tau_crit_expect))
    print()
    #Combiend biaxial and shear test
    print('The combined shear and biaxial test resulted in the following values')
    print('A reserve factor of: '+str(combinedReserveFactor))
    print('The test comes out to be: '+str(combinedReserveFactor==combinedReserveFactor_expect))