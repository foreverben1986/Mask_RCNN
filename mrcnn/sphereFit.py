
from scipy import optimize
import numpy as np

def fit(points):
    x = points[0]
    y = points[1]
    z = points[2]
    x_m = np.mean(x)
    y_m = np.mean(y)
    z_m = np.mean(z)


    def calc_R(xc, yc, zc):
        """ calculate the distance of each 3D points from the center (xc, yc) """
        return np.sqrt((x-xc)**2 + (y-yc)**2 + (z-zc)**2)


    def f_3(c):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        Ri = calc_R(*c)
        return Ri - Ri.mean()


    center_estimate = x_m, y_m, z_m
    center_3, ier = optimize.leastsq(f_3, center_estimate)

    xc_3, yc_3, zc_3 = center_3
    Ri_3 = calc_R(*center_3)
    R_3 = Ri_3.mean()
    residu_3 = sum((Ri_3 - R_3)**2)
    return (center_3, R_3)

######################
# sphere fit test
######################
# x = [1,1,1,1,-1,-1,-1,-1]
# y = [1,1,-1,-1,1,1,-1,-1]
# z = [1,-1,1,-1,1,-1,1,-1]
# print(fit((x,y,z)))
