import numpy as np

__X_BIAS__ = 0
__Y_BIAS__ = 0

__CAMERA_MATRIX__ = np.array([ \
    [1,0,0], \
    [0,1,0], \
    [0,0,1]])


__ARM_MATRIX_1__ = np.array([ \
    [1,0,0], \
    [0,1,0], \
    [0,0,1]])
               
__ARM_MATRIX_2__ = np.array([ \
    [1,0,0], \
    [0,1,0.5], \
    [0,0,0.866]])
               
__ARM_MATRIX_3__ = np.array([ \
    [1,0,0], \
    [0,1,0.707], \
    [0,0,0.707]])

__ARM_MATRIX__ = __ARM_MATRIX_3__

__TRANSITION_MATRIX__ = np.array([ \
    [1,0,0,-__X_BIAS__], \
    [0,1,0,-__Y_BIAS__], \
    [0,0,1,0], \
    [0,0,0,1]])

def projectCamera2Arm(data):
    coord = np.array([data[0], data[1], data[2], 1]).reshape(4,1)
    coord = np.dot(__TRANSITION_MATRIX__, coord)
    coord = coord[0:3, :]
    coord = np.dot(np.linalg.inv(__ARM_MATRIX__), coord)
    return (coord[0,0],coord[1,0],coord[2,0],data[3])