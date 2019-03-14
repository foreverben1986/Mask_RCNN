from scipy import optimize
import numpy as np

def fit(points):
    x = points[0]
    y = points[1]
    x_m = np.mean(x)
    y_m = np.mean(y)


    def calc_R(xc, yc):
        """ calculate the distance of each 2D points from the center (xc, yc) """
        return np.sqrt((x-xc)**2 + (y-yc)**2)


    def f_2(c):
        """ calculate the algebraic distance between the data points and the mean circle centered at c=(xc, yc) """
        Ri = calc_R(*c)
        return Ri - Ri.mean()


    center_estimate = x_m, y_m
    center_2, ier = optimize.leastsq(f_2, center_estimate)

    xc_2, yc_2 = center_2
    Ri_2 = calc_R(*center_2)
    R_2 = Ri_2.mean()
    residu_2 = sum((Ri_2 - R_2)**2)
    return (center_2, R_2)

def biasTotal(xy, circleParam):
#     radiusRes = ((xy[0] - circleParam[0][0])**2 + \
#             (xy[1] - circleParam[0][1])**2 - \
#                 circleParam[1]**2)
#     radiusRes[radiusRes <= 0] = 1
#     radiusRes[radiusRes > 0] = 0
#     inCircle = np.sum(radiusRes)
#     res = np.sum(np.square((xy[0] - circleParam[0][0])**2 + \
#         (xy[1] - circleParam[0][1])**2 - \
#             circleParam[1]**2))
#     if inCircle == 0:
#         return 9999999.
#     return 1/inCircle
    return np.sum(np.square((xy[0] - circleParam[0][0])**2 + \
        (xy[1] - circleParam[0][1])**2 - \
            circleParam[1]**2))

def biasCompare(xy, cp1, cp2):
    bias1 = biasTotal(xy, cp1)
    bias2 = biasTotal(xy, cp2)
    if bias1 < bias2:
        return -1
    elif bias1 > bias2:
        return 1
    else:
        return 0