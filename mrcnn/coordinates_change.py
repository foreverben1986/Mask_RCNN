import numpy as np

"""
arm biases in 30 degrees camera 
"""
__X_BIAS__ = 0.0693
__Y_BIAS__ = 0.220
# __Z_BIAS__ = 0.158 
__Z_BIAS__ = 0.108

"""
30 degrees camera based on horizon camera
"""
__CAMERA2_MATRIX__ = np.array([ \
    [1,0,0], \
    [0,0.866,-0.5], \
    [0,0.5,0.866]])

"""
30 degrees camera biases in horizon camera
"""
#Temp modify. To recover in funture
# __X_BIAS_2__ = 0.005
__X_BIAS_2__ = -0.005
__Y_BIAS_2__ = -0.650
# __Z_BIAS_2__ = 0.08
__Z_BIAS_2__ = 0.03


"""
30 degrees camera 
"""
__CAMERA_MATRIX__ = np.array([ \
    [1,0,0], \
    [0,1,0], \
    [0,0,1]])


__ARM_MATRIX_1__ = np.array([ \
    [1,0,0], \
    [0,1,0], \
    [0,0,1]])
             
"""
arm based on z-aixs 30 degrees camera
"""
__ARM_MATRIX_2__ = np.array([ \
    [1,0,0], \
    [0,1,0.5], \
    [0,0,0.866]])
              
"""
arm based on z-aixs 45 degrees camera
""" 
__ARM_MATRIX_3__ = np.array([ \
    [1,0,0], \
    [0,1,0.707], \
    [0,0,0.707]])

"""
arm based on z-aixs 30 degrees camera
"""
__ARM_MATRIX_4__ = np.array([ \
    [1,0,0], \
    [0,0.866,0], \
    [0,0.5,1]])

__ARM_MATRIX__ = __ARM_MATRIX_4__

__TRANSITION_MATRIX__ = np.array([ \
    [1,0,0,-__X_BIAS__], \
    [0,1,0,-__Y_BIAS__], \
    [0,0,1,-__Z_BIAS__], \
    [0,0,0,1]])

"""
The origin point coordinate of ARM in CAMERA:
__X_BIAS__ = x 
__Y_BIAS__ = y
"""

def projectCamera2_2_camera(data, current_point):
    __TRANSITION_MATRIX_2__ = np.array([ \
        [1,0,0,-__X_BIAS_2__], \
#         [0,1,0,-(__Y_BIAS_2__ + current_point[1])], \
        [0,1,0,-__Y_BIAS_2__], \
        [0,0,1,-__Z_BIAS_2__], \
        [0,0,0,1]])
    coord = np.array([data[0], data[1], data[2], 1]).reshape(4,1)
    coord = np.dot(__TRANSITION_MATRIX_2__, coord)
    coord = coord[0:3, :]
    coord = np.dot(__CAMERA2_MATRIX__, coord)
#     return (coord[0,0],coord[1,0],biasInDepth(coord[2,0]),data[3])
    return (coord[0,0],coord[1,0],coord[2,0],data[3])

def projectCamera2Arm(data):
    coord = np.array([data[0], data[1], data[2]]).reshape(3,1)
    coord = np.dot(np.linalg.inv(__ARM_MATRIX__), coord)
    coord = np.array([coord[0, 0], coord[1, 0], coord[2,0], 1]).reshape(4,1)
    coord = np.dot(__TRANSITION_MATRIX__, coord)
    coord = coord[0:3, :]
    return (coord[0,0],coord[1,0],biasInDepth(coord[2,0]),data[3])
#     return (coord[0,0],coord[1,0],coord[2,0],data[3])

def projectCoord(data,current_point):
    return projectCamera2Arm(projectCamera2_2_camera(data,current_point))

def biasInDepth(z):
    if z > 1.1:
        return z + 0.06
    elif z > 1:
        return z + 0.06
    elif z > 0.9:
        return z + 0.025
    elif z > 0.8:
        return z + 0.010
    else:
        return z

def coordinateMerge(relativePoint, machinePoint):
    return (relativePoint[0] + machinePoint[0], \
            relativePoint[1] + machinePoint[1], \
            relativePoint[2])


def coordinateMergeZ(relativePoint, machinePoint):
    return (machinePoint[0], \
            machinePoint[1], \
            relativePoint[2])