import math
# Calculate the fiber fracture FF
def fiberFracture(sigma_1, R_p_c, R_p_t):
    if sigma_1 > 0:
        exposure = sigma_1/R_p_t
    else:
        exposure = abs(sigma_1/R_p_c)
    RF = 1/exposure
    return RF
#Calculate the inter fiber fracture IFF
# Function for calculating mode A
def modeA(tau_21, sigma_2, R_rp, R_r_t, p_rp_t):
    exposure = math.sqrt((tau_21/R_rp)**2 + (1-p_rp_t*R_r_t/R_rp)**2 * (sigma_2/R_r_t)**2)+p_rp_t *sigma_2/R_rp
    RF = 1/exposure
    return RF

# Function for calculating mode B 
def modeB(tau_21, sigma_2, R_rp, p_rp_c):
    exposure = 1/R_rp * (math.sqrt(tau_21**2 + (p_rp_c*sigma_2)**2) + p_rp_c*sigma_2)
    RF=1/exposure
    return RF

# Function for calculating mode C
def modeC(tau_21, sigma_2, R_rp, R_r_c, p_rr_c):
    exposure = ((tau_21/(2*(1+p_rr_c)*R_rp))**2+(sigma_2/R_r_c)**2)*R_r_c/(-sigma_2)
    RF=1/exposure  
    return RF



def strength(row, R_p_t, R_p_c, R_r_c, R_r_t, R_rp, p_rp_c, 
             p_rp_t, p_rr_c, p_rr_t):
    mode = 'empty'
    #Build term for mode B, C transition
    R_rr_A = R_r_c/(2*(1+p_rr_c))
    tau_21_c = R_rp * math.sqrt(1+2*p_rp_c*(R_rr_A/R_rp))
    criterion = R_rr_A/abs(tau_21_c)
    # Check which mode to apply 
    if row['Normal_2'] >= 0:
        RF_IFF = modeA(tau_21=row['Shear_12'], sigma_2=row['Normal_2'], R_rp=R_rp, R_r_t=R_r_t, p_rp_t=p_rp_t)
        mode='A'
    elif abs(row['Normal_2']/row['Shear_12']) <= criterion:
        RF_IFF = modeB(tau_21=row['Shear_12'], sigma_2=row['Normal_2'], R_rp=R_rp, p_rp_c=p_rp_c)
        mode='B'
    else:
        RF_IFF = modeC(tau_21=row['Shear_12'], sigma_2=row['Normal_2'], R_rp=R_rp, R_r_c=R_r_c, p_rr_c=p_rr_c)
        mode='C'
    RF_FF = fiberFracture(sigma_1=row['Normal_1'], R_p_c=R_p_c, R_p_t=R_p_t)
    return mode, RF_IFF, RF_FF