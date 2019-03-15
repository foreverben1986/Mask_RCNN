from mrcnn import appleFit
import numpy as np
import matplotlib.pyplot as plt 
import matplotlib.image as mpimg 
import matplotlib.patches as patches
import time
import json
import os

__DEPTH_MIN__ = 0.2
__DEPTH_MAX__ = 3.
__DEPTH_BIAS__ = 0.4 #meter

def loadJson(path):
    with open(path) as f:
        data = json.load(f)
        return data
"""
depth: meter
xy: point(x, y)
instri: intrinsics as json
"""
def rs2DeprojectPixel2Point(instri, xy, depth):
    x = (xy[0] - instri["ppx"])/instri["fx"]
    y = (xy[1] - instri["ppy"])/instri["fy"]
    r2  = x*x + y*y
    coeffs = instri["coeffs"]
    f = 1 + coeffs[0]*r2 + coeffs[1]*r2*r2 + coeffs[4]*r2*r2*r2
    ux = x*f + 2*coeffs[2]*x*y + coeffs[3]*(r2 + 2*x*x)
    uy = y*f + 2*coeffs[3]*x*y + coeffs[2]*(r2 + 2*y*y)
    x = ux
    y = uy
    return (depth*x, depth*y, depth)

"""
depthImg: shape(x,y)
maskImg: shape(x,y,instance_num)
scale: device_scale
"""
def meanDepth(depthImg, maskImg, scale):
    depthImg = depthImg * 2**16 * scale
    depthImg = maskImg * depthImg[:,:,None]
    depthImg = depthImg * ((depthImg > __DEPTH_MIN__) & (depthImg < __DEPTH_MAX__))
    depthImgSum = np.sum(depthImg, (0, 1))
    indexSum = np.sum((depthImg > __DEPTH_MIN__) & (depthImg < __DEPTH_MAX__), (0, 1))
    return depthImgSum/indexSum

"""
maskImg: shape(x,y,instance_num)
"""
def maskArea(maskImg):
    return np.sum(maskImg, (0, 1))

def rs2DeprojectMask2Points(instri, mask, depthImg):
    depthImg = depthImg * 2**16 * instri["scale"]
    depthImg[mask==0] = 0
    median = np.median(depthImg)
    maxDepth = median + __DEPTH_BIAS__
    minDepth = median - __DEPTH_BIAS__
    depthImg[(depthImg < minDepth) & (depthImg > maxDepth)] = 0
    xy = np.nonzero(depthImg)
    xs = np.array([])
    ys = np.array([])
    zs = np.array([])
    for i in range(len(xy[0])):
        row = xy[0][i]
        col = xy[1][i]
        depth = depthImg[row, col]
        x,y,z = rs2DeprojectPixel2Point(instri, (col, row), depth)
        xs = np.append(xs, x)
        ys = np.append(ys, y)
        zs = np.append(zs, z)
    return (xs,ys,zs)
        
##############################
# rs2DeprojectPixel2Point test
##############################
# xy = (1238, 380)
# data1 = loadJson('./test_img/depth_151552316342.json')
# imgDepth1 = mpimg.imread("./test_img/depth_151552316342.png") 
# depth1 = imgDepth1[xy[1], xy[0]] * 2**16 * 0.001
# print(depth1)
# print(rs2DeprojectPixel2Point(data1, xy, depth1))

##############################
# meanDepth test
##############################
# depthImg = np.random.random((3, 3))/(2**16)
# maskImg = np.zeros((3, 3, 3))
# maskImg[0:2,0:2,:]=1
# print(depthImg)
# test = maskImg*depthImg[:,:,None]
# print(meanDepth(depthImg, maskImg, 1))

"""
output 3d point coordinates to assigned path
"""
def outputTarget(result, path):
    now = time.time()*100
    with open(os.path.join(path,str(now)+".txt"), 'w') as f:
        for point in result:
            f.write(str(point[0]) + "," + str(point[1]) + "," + str(point[2]) + "," + str(point[3]))
            f.write("\n")
        f.write("end")

########################
# outputTarget test
########################
# a = [(1,2,3),(3,2,1),(1,2,3)]
# path = "./test_txt"
# outputTarget(a, path)