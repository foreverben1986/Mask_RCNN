from mrcnn import apple_tool as atool
from mrcnn import appleFit
import numpy as np
import os
from mrcnn import sphereFit
from mrcnn import coordinates_change as cdc
import logging


# Root directory of the project
ROOT_DIR = os.path.abspath("../")
potinOutputPath = os.path.join(ROOT_DIR, "targets")

__X_Y_Z_RANGE__ = {"xmin":0, "ymin":0, "xmax":0.6, "ymax":0.320, "zmin":0, "zmax":1.200}

"""
use circle fit to fit the mask image
boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
masks: [height, width, num_instances]
depthImg: depth img
intrinsics: intrinsics
"""
def fit1(boxes, masks, depthImg, intrinsics):
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
        print("we should go!")
    else:
        assert boxes.shape[0] == masks.shape[-1]
    # meanDepths: [number_of_instances] 
    meanDepths = atool.meanDepth(depthImg,masks,intrinsics["scale"])
    # area: [number_of_instances]
    maskAreas = atool.maskArea(masks)
    orders = sortMasks(meanDepths, maskAreas)
    masks = masks[:,:,orders]
    result = []
    for i in range(N):
        # first circle
        mask = masks[:,:,i]
        padded_mask = np.zeros(
                (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        circleDatas = appleFit.fit(padded_mask)
        pointsPixel = []
        k = 1
        for circleData in circleDatas:
            circleRow = circleData[0][0] - 1
            circleCol = circleData[0][1] - 1
            radius = circleData[1]
            if circleRow == -100:
                break
            pointsPixel.append((circleRow,circleCol))
            k+=1
            if k==3:
                break
        if len(pointsPixel)>0:
            for pointPixel in pointsPixel:
                x,y,z = atool.rs2DeprojectPixel2Point(intrinsics, \
                            (pointPixel[1],pointPixel[0]), \
                            meanDepths[i])
                #TODO remove the failed x,y,z
                result.append((x,y,z,radius/intrinsics["fx"]*meanDepths[i]))
        # if there is one result point to pick up, stop filter
        # if len(result) > 0:
        #     break
    if len(result) < 1:
        print("we need to go")
    else:
        atool.outputTarget(result, potinOutputPath)


"""
use sphere fit to fit the mask image
boxes: [num_instance, (y1, x1, y2, x2, class_id)] in image coordinates.
masks: [height, width, num_instances]
depthImg: depth img
intrinsics: intrinsics
"""
def fit2(boxes, masks, depthImg, intrinsics, depth_scale=0.001, blackList=[], current_point=(0,0,0)):
    # Number of instances
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
        print("we should go!")
    else:
        assert boxes.shape[0] == masks.shape[-1]
    # meanDepths: [number_of_instances] 
    meanDepths = atool.meanDepth(depthImg,masks,depth_scale)
    # area: [number_of_instances]
    maskAreas = atool.maskArea(masks)
    orders = sortMasks(meanDepths, maskAreas)
    masks = masks[:,:,orders]
    result = []
    for i in range(N):
        # first circle
        mask = masks[:,:,i]

        points = atool.rs2DeprojectMask2Points(intrinsics, mask, depthImg, depth_scale)
        if len(points[0]) > 150:
            (x,y,z), radius = sphereFit.fit(points)
        else:
            logging.debug("the number of pixel of the apple is no more than 150...")
            (x,y,z), radius = \
                    ((np.mean(points[0]),\
                     np.mean(points[1]),\
                     np.mean(points[2])),\
                     0.05)
        # change the coordinates from camera to arms
        logging.debug("apple in camera system is at %s.", (x,y,z, radius))
        x,y,z,radius = cdc.projectCamera2Arm((x,y,z,radius))
        
        # apple radius between 1cm and 9cm & 
        # remove the failed x,y,z
#         if (radius > 0.01) & (radius < 0.09) & isInRange((x,y,z), current_point):
        if (radius > 0.01) & (radius < 0.09) & isInRange((x,y,z), current_point):
            if not atool.isInBlackList(cdc.coordinateMerge((x,y,z), current_point), blackList):
                result.append((x,y,z,radius))
            else:
                logging.debug("apple is in black list.")
        else:
            logging.debug("apple is out of range.")
            
        # output the 1st one
        if len(result) > 0:
            break

    if len(result) < 1:
        print("we need to go")
    else:
        return result[0]


def isInRange(relative_point, current_point):
    logging.debug("current_point is at %s.", current_point)
    point = (current_point[0] + relative_point[0], \
             current_point[1] + relative_point[1], \
             relative_point[2], \
            )
    logging.debug("pick point is at %s.", point)
    return (point[0] > __X_Y_Z_RANGE__["xmin"]) & (point[0] < __X_Y_Z_RANGE__["xmax"]) \
        & (point[1] > __X_Y_Z_RANGE__["ymin"]) & (point[1] < __X_Y_Z_RANGE__["ymax"]) \
        & (point[2] > __X_Y_Z_RANGE__["zmin"]) & (point[2] < __X_Y_Z_RANGE__["zmax"])

"""
meanDepth: [number_of_instances]
maskArea: [number_of_instances]
"""
def sortMasks(meanDepth, maskArea):
    factor = np.divide(meanDepth, maskArea, dtype=float)
    return np.argsort(factor)

######################
# test sortMasks
######################
# a = np.array([1,2,3,4,5])
# b = np.array([31,12,93,24,15])
# print(sortMasks(a,b))