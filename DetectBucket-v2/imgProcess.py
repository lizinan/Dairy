from posix import ST_SYNCHRONOUS
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


def process(color_image,cropLocation,n):
    #### 得到轮廓 ####
    crop = color_image[cropLocation[1]:cropLocation[3],cropLocation[0]:cropLocation[2]]
    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
    cv2.imshow('%dhsvFrame'%n,hsvFrame)

    lowerHSV = np.array([100, 100, 70])
    upperHSV = np.array([130, 255, 255])
    blueMask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)

    blueBlur = cv2.medianBlur(blueMask,3)

    blueKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    blueClose = cv2.morphologyEx(blueBlur, cv2.MORPH_CLOSE,blueKernel)

    blueContours, hierarchy = cv2.findContours(blueClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

    redlowerHSV = np.array([0, 155, 100])
    redupperHSV = np.array([15, 255, 180])
    redMask = cv2.inRange(hsvFrame,redlowerHSV,redupperHSV)

    redBlur = cv2.medianBlur(redMask,3)

    redKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    redClose = cv2.morphologyEx(redBlur, cv2.MORPH_CLOSE,redKernel)

    #### DEBUG ####
    # cv2.imshow('redinRange',redMask)
    # cv2.imshow('redblur',redBlur)
    cv2.imshow('%dredOpen'%n,redClose)
    # cv2.imshow("blueinrange",blueMask)
    # cv2.imshow("blueBlur",blueBlur)
    cv2.imshow("%dblueClose"%n,blueClose)

    redContours, hierarchy = cv2.findContours(redClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

        
#### situation judge #### 
    pixels = [0,0]
    states = [0,0]
    
    maxRedArea = 0
    maxBlueArea = 0
    maxRedIndex = 0
    maxBlueIndex = 0
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
            redRectPoint = sorted(redRectPoint, key= lambda s:(s[0], -s[1]))
            redRectPoint = np.int0(redRectPoint)
            pixels[0] = [round(redRect[0][0]) + cropLocation[0],round(redRect[0][1]) + cropLocation[1]]

    if blueContours != []:
        for i in range(len(blueContours)):
            area = cv2.contourArea(blueContours[i])
            if area > maxBlueArea:
                maxBlueArea = area
                maxBlueIndex = i
        if maxBlueArea > 20:
            blueRect = cv2.minAreaRect(blueContours[maxBlueIndex])
            blueRectPoint = cv2.boxPoints(blueRect)
            blueRectPoint = sorted(blueRectPoint, key= lambda s:(s[0], -s[1])) 
            blueRectPoint = np.int0(blueRectPoint)
            pixels[1] = [round(blueRect[0][0]) + cropLocation[0], round(blueRect[0][1]) + cropLocation[1]]
    
    if pixels[0] == 0 and pixels[1] == 0: ####没有识别到
        return pixels,states

    if pixels[0] == 0 and pixels[1]!= 0:#### 红色完全遮挡
        states[1] = 1
        return pixels,states

    if pixels[1] == 0 and pixels[0] != 0:#### 蓝色完全遮挡
        states[0] = 1
        return pixels,states
        
    #### 对图像进行与操作  ####
    redImg = np.zeros(((cropLocation[3] - cropLocation[1]),(cropLocation[2] - cropLocation[0]),3),np.uint8)
    blueImg = np.zeros(((cropLocation[3] - cropLocation[1]),(cropLocation[2] - cropLocation[0]),3),np.uint8)
    # redImg = np.zeros((640,480,3),np.uint8)
    # blueImg = np.zeros((640,480,3),np.uint8)

    cv2.rectangle(redImg,(redRectPoint[0][0] - 2,redRectPoint[0][1]),(redRectPoint[3][0] + 2,redRectPoint[3][1]),color=(255,255,255),thickness=-1)
    cv2.rectangle(blueImg,(blueRectPoint[0][0] -2,blueRectPoint[0][1]),(blueRectPoint[3][0] + 2,blueRectPoint[3][1]),color=(255,255,255),thickness=-1)
    redAndBlue = cv2.bitwise_and(redImg,blueImg)
    redAndBlue = cv2.cvtColor(redAndBlue,cv2.COLOR_BGR2GRAY)
    cv2.imshow("%dredImg"%n,redImg)
    cv2.imshow("%dblueImg"%n,blueImg)
    cv2.imshow("%dredAndBlue"%n,redAndBlue)

    overlap = len(redAndBlue[redAndBlue > 0])
    print("%doverlap!!"%n,overlap)
    if overlap < 10: #### 红蓝桶的斜率可以直接得到 ####
        states[0] = 1
        states[1] = 1
        return pixels,states
    else:
        if maxBlueArea > maxRedArea:#### 蓝桶斜率可以直接由餐盘坐标系得到，红桶斜率需要转换 ####
            states[1] = 1
        else:#### 红桶斜率可以直接由餐盘坐标系得到，蓝桶斜率需要转换 ####
            states[0] = 1
        return pixels,states


