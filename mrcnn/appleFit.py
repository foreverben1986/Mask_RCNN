import matplotlib.pyplot as plt 
import matplotlib.image as mpimg 
import matplotlib.patches as patches
import numpy as np
import sys
import math
from mrcnn import circleFit
import functools as fct

# polygon number of sides
__NUMBER_OF_SIDES__=40
# maximum angle degree
__MAX_ALLOW_DEGREE__=30
# minimun continuous points
__MIN_CONTINUOUS_POINTS__=5
# maximum apple radius (pixel)
__MAX_APPLE_RADIUS__ = 150
# minimum apple radius (pixel)
__MIN_APPLE_RADIUS__ = 10

# for log
#np.set_printoptions(threshold=np.inf)

# # load
# img = mpimg.imread("./test_img/test5.png") 

# # copy img to work
# imgWork = np.array(img)

# # sum the RGB
# imgWork = np.sum(imgWork, axis=-1)

def fit(maskImg):
    """
    edgeDetect
    @return tuple((xpoints, ypoints))
    """
    def edgeDetect(maskImg):
        maskImg[maskImg == 4] = 0
        maskImg[maskImg > 0] = 1
        temp = np.multiply(np.gradient(maskImg), maskImg > 0)
        xySum = np.sum(np.abs(temp), axis=0)
        return np.nonzero(xySum), temp

    """
    cCountinuous
    resort the points clockwise or anti-clockwise
    @pointsData tuple((xpoints, ypoints), edge normal value)
    @return (xpoints, ypoints)
    """
    def cCountinous(pointsData):
        if type(pointsData) == tuple:
            points = pointsData[0]
            if len(points) == 2:
                if len(points[0]) < 1:
                    return (np.array([]),np.array([]))
                lastPoint = points[0][0], points[1][0]
                pointsResult = points[0][:1], points[1][:1]
                points = points[0][1:], points[1][1:]
                while points[0].size > 0:
                    lastPointRow = lastPoint[0]
                    lastPointCol = lastPoint[1]
                    pointsRow = points[0]
                    pointsCol = points[1]
                    offset = np.ndarray(0)
                    base = np.ndarray(0)
                    if len(np.nonzero(offset)[0]) == 0:
                        # east
                        colTargets = pointsCol == lastPointCol + 1
                        base = colTargets
                        rowTargets = pointsRow[base] == lastPointRow
                        offset = rowTargets
                    if len(np.nonzero(offset)[0]) == 0:
                        # south-east
                        rowTargets = pointsRow[base] == lastPointRow + 1
                        offset = rowTargets
                    if len(np.nonzero(offset)[0]) == 0:
                        # south
                        rowTargets = pointsRow == lastPointRow + 1
                        base = rowTargets
                        colTargets = pointsCol[base] == lastPointCol
                        offset = colTargets 
                    if len(np.nonzero(offset)[0]) == 0:
                        # south-west
                        colTargets = pointsCol[base] == lastPointCol - 1
                        offset = colTargets 
                    if len(np.nonzero(offset)[0]) == 0:
                        # west
                        colTargets = pointsCol == lastPointCol - 1
                        base = colTargets
                        rowTargets = pointsRow[base] == lastPointRow
                        offset = rowTargets
                    if len(np.nonzero(offset)[0]) == 0:
                        # north-west
                        rowTargets = pointsRow[base] == lastPointRow - 1
                        offset = rowTargets
                    if len(np.nonzero(offset)[0]) == 0:
                        # north
                        rowTargets = pointsRow == (lastPointRow - 1)
                        base = rowTargets
                        colTargets = pointsCol[base] == lastPointCol
                        offset = colTargets 
                    if len(np.nonzero(offset)[0]) == 0:
                        # north-east
                        colTargets = pointsCol[base] == lastPointCol + 1
                        offset = colTargets
                    if len(np.nonzero(offset)[0]) > 0:
                    #     print("==========")
                    #     print(pointsResult[0][-1])
                    #     print(pointsResult[1][-1])
                    #     print(base)
                    #     print(offset)
                        baseTrueIndex = np.nonzero(base)[0]
                        offsetTrueIndex = np.nonzero(offset)[0]
                        index = baseTrueIndex[offsetTrueIndex]
                        curPoint = pointsRow[index], pointsCol[index]
                        pointsResult = np.append(pointsResult[0], curPoint[0]), \
                                np.append(pointsResult[1], curPoint[1])
                        points = np.delete(pointsRow, index), np.delete(pointsCol, index)
                        lastPoint = curPoint
                    else:
                        break
                return pointsResult

    pointsData = edgeDetect(maskImg)
    if len(pointsData) > 0:
        points = cCountinous(pointsData)

    #######################
    # segment points
    #######################
    print("points:", len(points[0]))
    step = int(len(points[0])/__NUMBER_OF_SIDES__)
    circleDatas = []
    if step != 0:
        # draw the selected points
        points = points[0][::step], points[1][::step]
        if len(points[0])%__NUMBER_OF_SIDES__ < 10:
            points = points[0][:-2], points[1][:-2]


        # get vector
        pointsMoveLeft1 = np.append(points[0][1:], points[0][0]), np.append(points[1][1:], points[1][0])
        vector = pointsMoveLeft1[0] - points[0], pointsMoveLeft1[1] - points[1]
        vectorMoveLeft1 = np.append(vector[0][1:], vector[0][0]), np.append(vector[1][1:], vector[1][0])
        vectorMor = np.sqrt(np.add(np.square(vector[0]), np.square(vector[1])))
        vectorMorMoveLeft1 = np.append(vectorMor[1:], vectorMor[0])
        vectorInnerProduct = np.add(np.multiply(vector[0], vectorMoveLeft1[0]), np.multiply(vector[1], vectorMoveLeft1[1]))
        cosTheta = np.divide(vectorInnerProduct, np.multiply(vectorMor, vectorMorMoveLeft1))
        cosTheta[cosTheta >= 1] = 1
        #find odd points
        degrees = np.arccos(cosTheta) / np.pi * 180
        oddPoints = np.nonzero(degrees > __MAX_ALLOW_DEGREE__)[0]
        pointGroups = []
        oddPoints = oddPoints.flatten()
        i = 0
        while i < (len(oddPoints) - 1):
            pointGroup = points[0][(oddPoints[i]+1):(oddPoints[i+1]+1)], points[1][(oddPoints[i]+1):(oddPoints[i+1]+1)]
            pointGroups.append(pointGroup)
            i+=1

        if len(oddPoints) >0:
            lastGroup = np.append(points[0][oddPoints[-1]+2:], points[0][:oddPoints[0]+2]), \
                    np.append(points[1][oddPoints[-1]+2:], points[1][:oddPoints[0]+2])
            pointGroups.append(lastGroup)
        else:
            print("no oddPoints")
            pointGroups.append(points)

        # filter the group in which there are above 5 points
        ############################
        # fit circle and filter them
        ############################
        for pointGroup in pointGroups:
            if len(pointGroup[0]) >= __MIN_CONTINUOUS_POINTS__:
                circleParam = circleFit.fit(pointGroup)
                if (circleParam[1] < __MAX_APPLE_RADIUS__) & (circleParam[1] > __MIN_APPLE_RADIUS__):
                    circleDatas.append(circleFit.fit(pointGroup))

    if len(circleDatas) > 0:
        cmpSelf=fct.partial(circleFit.biasCompare,points)
        circleDatas.sort(key=fct.cmp_to_key(cmpSelf))
        return circleDatas
    else:
        pointsData = np.nonzero(maskImg)
        row = -99
        col = -99
        if len(pointsData[0]) > 0:
            row = np.mean(pointsData[0])
            col = np.mean(pointsData[1])
        return [((row, col), 0)]

    #######################
    # draw image
    #######################
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.imshow(img, origin="upper")
    # color = 0x0000ff
    # i = 0
    # for circleData in circleDatas:
    #     colorStr = "#" + hex(color)[2:].zfill(6)
    #     print(circleData)
    #     print(circleFit.biasTotal(points, circleData))
    #     if i==0:
    #         ax.add_patch(patches.Circle((circleData[0][1], circleData[0][0]), circleData[1], edgeColor='r', fill=False))
    #     else:
    #         ax.add_patch(patches.Circle((circleData[0][1], circleData[0][0]), circleData[1], edgeColor=colorStr, fill=False))
    #     color+=100
    #     i+=1

    # ax.scatter(points[1], points[0], s=1, c='g')

    # plt.show()
