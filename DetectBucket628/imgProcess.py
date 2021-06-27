import numpy as np
import cv2

def decidePlayer(img):
    w = 640
    h = 480

#### init params ####
    redPlayer = 0
    bluePlayer = 1

    redLowerHsv = np.array([0,0,0])
    redUpperHsv = np.array([255,255,255])

    blueLowerHsv = np.array([0,0,0])
    blueUpperHsv = np.array([255,255,255])

    crop = img[0:h/3,0:w]

    hsvCrop = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)    

#### refine red ####
    redMask = cv2.inRange(hsvCrop,redLowerHsv,redUpperHsv)
    redBlur = cv2.medianBlur(redMask,3)
    redKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    redOpen = cv2.morphologyEx(redBlur, cv2.MORPH_OPEN,redKernel)
    redContours, hierarchy = cv2.findContours(redOpen,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

    if redContours == []:
        return bluePlayer

#### refine blue ####
    blueMask = cv2.inRange(hsvCrop,blueLowerHsv,blueUpperHsv)    
    blueBlur = cv2.medianBlur(blueMask,3)
    blueKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    blueClose = cv2.morphologyEx(blueBlur, cv2.MORPH_CLOSE,blueKernel)
    blueContours, hierarchy = cv2.findContours(blueClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

    if blueContours == []:
        return redPlayer

#### compare ####
    maxRedArea = 0
    maxBlueArea = 0
    for i in range(len(redContours)):
        area = cv2.contourArea(redContours[i])
        if area > maxRedArea:
            maxRedArea = area

    for i in range(len(blueContours)):
        area = cv2.contourArea(blueContours[i])
        if area > maxBlueArea:
            maxBlueArea = area
    if maxRedArea > maxBlueArea:
        return redPlayer
    else:
        return bluePlayer


def process(img,x,y,n):
    #### 得到轮廓 ####
    hsvFrame = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    cv2.imshow('%dhsvFrame'%n,hsvFrame)

    lowerHSV = np.array([100, 100, 70])
    upperHSV = np.array([130, 255, 255])
    blueMask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)
    # cv2.imshow("blueinrange",blueMask)

    blueBlur = cv2.medianBlur(blueMask,3)
    # cv2.imshow("blueBlur",blueBlur)

    blueKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    blueClose = cv2.morphologyEx(blueBlur, cv2.MORPH_CLOSE,blueKernel)
    cv2.imshow("%dblueClose"%n,blueClose)

    blueContours, hierarchy = cv2.findContours(blueClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

    redlowerHSV = np.array([0, 150, 100])
    redupperHSV = np.array([30, 255, 150])

    redMask = cv2.inRange(hsvFrame,redlowerHSV,redupperHSV)
    # cv2.imshow('redinRange',redMask)

    redBlur = cv2.medianBlur(redMask,3)
    # cv2.imshow('redblur',redBlur)

    redKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    redClose = cv2.morphologyEx(redBlur, cv2.MORPH_CLOSE,redKernel)
    cv2.imshow('%dredOpen'%n,redClose)

    redContours, hierarchy = cv2.findContours(redClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

        
#### situation judge #### 应该先过滤小面积，同时应该留一点重叠空间

    redPixel = []
    bluePixel = []
    redFlag = 0 #### 0  远端， 1 近端
    blueFlag = 0
    maxRedArea = 0
    maxBlueArea = 0
    maxRedIndex = 0
    maxBlueIndex = 0
    bucket = 0
    blueRect = []
    redRect = []

    if redContours != []:
        for i in range(len(redContours)):
            area = cv2.contourArea(redContours[i])
            if area > maxRedArea:
                maxRedArea = area
                maxRedIndex = i
        if maxRedArea > 20:
            redRect = cv2.minAreaRect(redContours[maxRedIndex])
            redRectPoint = cv2.boxPoints(redRect)
            redRectPoint = sorted(redRectPoint, key= lambda s:(s[0], -s[1])) #### 按y,x排序 ####
            redRectPoint = np.int0(redRectPoint)
            redPixel = [round(redRect[0][0]) + x,round(redRect[0][1]) + y]

    if blueContours != []:
        for i in range(len(blueContours)):
            area = cv2.contourArea(blueContours[i])
            if area > maxBlueArea:
                maxBlueArea = area
                maxBlueIndex = i
        if maxBlueArea > 20:
            blueRect = cv2.minAreaRect(blueContours[maxBlueIndex])
            blueRectPoint = cv2.boxPoints(blueRect)
            blueRectPoint = sorted(blueRectPoint, key= lambda s:(s[0], -s[1])) #### 按x,y排序 ####
            blueRectPoint = np.int0(blueRectPoint)
            bluePixel = [round(blueRect[0][0]) + x, round(blueRect[0][1]) + y ]
    
    if redPixel == [] and bluePixel == []: ####没有识别到
        return redPixel,bluePixel,redFlag,blueFlag,bucket
    if redPixel == [] and bluePixel != []:#### 红色完全遮挡
        bucket = 1
        blueFlag = 1
        return redPixel,bluePixel,redFlag,blueFlag,bucket
    if bluePixel == [] and redPixel != []:#### 蓝色完全遮挡
        bucket = 1
        redFlag = 1
        return redPixel,bluePixel,redFlag,blueFlag,bucket
        
    redImg = np.zeros((640,480,3),np.uint8)####黑色图
    blueImg = np.zeros((640,480,3),np.uint8)
    cv2.rectangle(redImg,redRectPoint[0],redRectPoint[3],color=(255,255,255),thickness=-1)
    cv2.rectangle(blueImg,blueRectPoint[0],blueRectPoint[3],color=(255,255,255),thickness=-1)
    redAndBlue = cv2.bitwise_and(redImg,blueImg)
    redAndBlue = cv2.cvtColor(redAndBlue,cv2.COLOR_BGR2GRAY)
    cv2.imshow("%dredImg"%n,redImg)
    cv2.imshow("%dblueImg"%n,blueImg)
    cv2.imshow("%dredAndBlue"%n,redAndBlue)

    overlap = len(redAndBlue[redAndBlue > 0])
    print("%doverlap!!"%n,overlap)
    if overlap < 10: #### 没有遮挡
        bucket = 2
        return redPixel,bluePixel,redFlag,blueFlag,bucket
    else:
        bucket = 1
        #### choose nearer bucket ####
        if maxBlueArea > maxRedArea:
            blueFlag = 1
            redPixel = []
        else:
            redFlag = 1
            bluePixel = []

    return redPixel,bluePixel,redFlag,blueFlag,bucket


