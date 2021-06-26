from random import sample
import numpy as np
import cv2


def process(color_img,x,y,w,h):
    #### 裁剪图片 ####
    crop = color_img[y:y+h, x:x+w]

    k = 1/3 # k值控制宽度裁剪，给1/3足够
    p = 1/2 # p值控制高度裁剪，应当尽量给大一些
    arrowNumbers = 0
    arrowInfo = []
    headNum = 0
    headCenter = []
    headWholePixel = []
    tailHalfNum = 0
    tailWholePixel = []
    if w/h > 4: # 控制yolo框，当宽长比较大，证明箭越水平，在图上位置也越居中，就不应当用对角处理
        leftCrop = crop[0:h,0:int(w*k)]
        rightCrop = crop[0:h,int(w*(1-k)):w]
        cropXY = [[0,0],[int(w*(1-k)),0]]
        smallCrops = [leftCrop,rightCrop]
        for i in range(2):
            headContours = getHeadContours(smallCrops[i])
            head_center,head_whole_pixel = getHeadInfo(headContours,cropXY[i][0],cropXY[i][1])
            if len(head_whole_pixel):
                tailContours = getTailContours(smallCrops[1 - i])
                tail_whole_pixel = getTailInfo(tailContours,cropXY[1 - i][0],cropXY[1- i][1])
                if len(tail_whole_pixel) :
                    headNum = headNum + len(head_whole_pixel)
                    tailHalfNum = tailHalfNum + len(tail_whole_pixel)
                    headCenter = headCenter + head_center
                    headWholePixel = headWholePixel + head_whole_pixel
                    tailWholePixel = tailWholePixel + tail_whole_pixel
    else:
        #### 裁剪四个角 ####
        ULcrop = crop[0:int(h*p),0:int(w*k)]
        DLcrop = crop[int(h*(1-p)):h,0:int(w*k)]
        URcrop = crop[0:int(p*h),int(w*(1-k)):w]
        DRcrop = crop[int(h*(1-p)):h,int(w*(1-k)):w]
        smallCrops = [ULcrop,URcrop,DRcrop,DLcrop]
        cropXY = [[0,0],[int(w*(1-k)),0],[int(w*(1-k)),int(h*(1-p))],[0,int(h*(1-p))]]
        for i in range(4):
            headContours = getHeadContours(smallCrops[i])
            head_center,head_whole_pixel = getHeadInfo(headContours,cropXY[i][0],cropXY[i][1])
            if len(head_whole_pixel):
                tailContours = getTailContours(smallCrops[(i+2)%4])
                tail_whole_pixel = getTailInfo(tailContours,cropXY[(i+2)%4][0],cropXY[(i+2)%4][1])
                tailContours = getTailContours(smallCrops[(i+2)%4])
                if len(tail_whole_pixel):
                    headNum = headNum + len(head_whole_pixel)
                    tailHalfNum = tailHalfNum + len(tail_whole_pixel)
                    headCenter = headCenter + head_center
                    headWholePixel = headWholePixel + head_whole_pixel
                    tailWholePixel = tailWholePixel + tail_whole_pixel

    ### DEBUG ####
    getHeadContours(crop)
    getTailContours(crop)
    #### 得到轮廓像素信息 ####
    #### headWholePixel索引方式：箭头轮廓序号？ min or max？ x or y？ ####
    #### tailWholePixel索引方式：箭羽轮廓序号？ min or max？ x or y？ ####
    if headNum == 0 or headNum > 2:
        return arrowNumbers,[]
    else:
        if tailHalfNum < 2 or tailHalfNum > 4:
            return arrowNumbers,[]

    
    headMinPixel = []
    headMaxPixel = []
    tailMinPixel = []
    tailMaxPixel = []
    if headNum == 1:
        headMinPixel = headWholePixel[0][0]
        headMaxPixel = headWholePixel[0][1]
        if tailHalfNum == 2:
            print("situation 1-2: one arrow and two half-tail")
            tailMinPixel = [(tailWholePixel[0][0][0] + tailWholePixel[1][0][0]) / 2, (tailWholePixel[0][0][1] + tailWholePixel[1][0][1]) / 2]
            tailMaxPixel = [(tailWholePixel[0][1][0] + tailWholePixel[1][1][0]) / 2, (tailWholePixel[0][1][1] + tailWholePixel[1][1][1]) / 2]
        elif tailHalfNum == 3:
            print("situation 1-3: one arrow and three half-tail")
            tailMinPixel,tailMaxPixel = selectTail(tailWholePixel)
        else:
            print("situation 1-4: one arrow and two tail")
            tailSides = classifyTail(tailWholePixel)
            tailK = [0,0]
            tailCenter = [0,0]
            k = [0,0]
            for i in range(2):
                if tailSides[i][1][0] != tailSides[i][0][0]:
                    tailK[i] = (tailSides[i][1][1]-tailSides[i][0][1])/ (tailSides[i][1][0]-tailSides[i][0][0])
                else:
                    tailK[i] = 10000
                tailCenter[i] = [(tailSides[i][0][0]+tailSides[i][1][0])/2,(tailSides[i][0][1]+tailSides[i][1][1])/2]

            k[0] = (tailCenter[0][1] - headCenter[0][1])/(tailCenter[0][0] - headCenter[0][0])
            k[1] = (tailCenter[1][1] - headCenter[0][1])/(tailCenter[1][0] - headCenter[0][0])

            if abs(k[0]-tailK[0]) < abs(k[1] - tailK[1]):
                tailMinPixel = tailSides[0][0]
                tailMaxPixel = tailSides[0][1]
            else:
                tailMinPixel = tailSides[1][0]
                tailMaxPixel = tailSides[1][1]
        arrowPixel = [[[headMinPixel,headMaxPixel],[tailMinPixel,tailMaxPixel]]]
    else:
        if tailHalfNum == 2:
            print("situation 2-2: 2 arrow and 2 half-tail")
            tailMinPixel = tailWholePixel[0][0]
            tailMaxPixel = tailWholePixel[0][1]
            arrowPixel = selectHead(tailMinPixel,tailMaxPixel,headCenter,headWholePixel)
        elif tailHalfNum == 3:
            print("situation 2-3: 2 arrow and 3 half-tail")  #### 有问题
            tailMinPixel,tailMaxPixel = selectTail(tailWholePixel)
            arrowPixel = selectHead(tailMinPixel,tailMaxPixel,headCenter,headWholePixel)
        else:
            print("situation 2-4: 2 arrow and 4 half-tail")
            tailSides = classifyTail(tailWholePixel)
            arrowPixel = classifyArrow(headCenter,headWholePixel,tailSides)
        
    print("arrowPixel",arrowPixel,x,y)
    arrowNumbers,arrowInfo = getArrowInfo(arrowPixel,x,y)

    #### DEBUG ####
    # k = 1/3
    # p = 1/2
    # if w/h > 4:
    #     p = 1
    # cv2.rectangle(crop, (0,0), (int(w*k),int(h*p)), (0,255,0), 3) #### start - end ####
    # cv2.rectangle(crop, (0,int(h*(1-p) )), (int(w*k),h), (255,0,0), 3)
    # cv2.rectangle(crop, (int(w*(1-k)),0), (w,int(p*h)), (0,0,255), 3)
    # cv2.rectangle(crop, (int(w*(1-k)),int(h*(1-p))), (w,h), (0,0,0), 3)
    # cv2.imshow("crop",crop)  

    return arrowNumbers,arrowInfo
    
    
#### 箭羽和箭头配对 ####
def selectHead(tailMinPixel,tailMaxPixel,headCenter,headWholePixel):
    tailCenterPixel = [(tailMinPixel[0]+tailMaxPixel[0])/2,(tailMinPixel[1]+tailMaxPixel[1])/2]
    tailLength = (tailMaxPixel[0] - tailMinPixel[0])*( tailMaxPixel[0] - tailMinPixel[0]) + (tailMaxPixel[1] - tailMinPixel[1])*( tailMaxPixel[1] - tailMinPixel[1])
    headTailDis0 = (tailCenterPixel[0] - headCenter[0][0])*(tailCenterPixel[0] - headCenter[0][0])
    headTailDis1 = (tailCenterPixel[0] - headCenter[1][0])*(tailCenterPixel[0] - headCenter[1][0])

    if headTailDis0 < 2*tailLength: #### 头尾接近
        headMinPixel = headWholePixel[1][0]
        headMaxPixel = headWholePixel[1][1]
    elif headTailDis1 < 2*tailLength: #### 头尾接近
            headMinPixel = headWholePixel[0][0]
            headMaxPixel = headWholePixel[0][1]        
    else: #### 尾巴同边，取最短
        if headTailDis0 < headTailDis1:
            headMinPixel = headWholePixel[0][0]
            headMaxPixel = headWholePixel[0][1]
        else:
            headMinPixel = headWholePixel[1][0]
            headMaxPixel = headWholePixel[1][1]
    # #### k0 箭尾斜率，k1 箭尾和箭头0,k2 箭尾和箭头1 ####
    # if tailMaxPixel[0] != tailMinPixel[0]:
    #     k0 = (tailMaxPixel[1] - tailMinPixel[1])/(tailMaxPixel[0] - tailMinPixel[0])
    # else:
    #     k0 = 10000
    # if tailCenterPixel[0] - headCenter[0][0] != 0:
    #     k1 = (tailCenterPixel[1] - headCenter[0][1])/(tailCenterPixel[0] - headCenter[0][0])
    # else:
    #     k1 = 10000
    # if tailCenterPixel[0] - headCenter[1][0] != 0:
    #     k2 = (tailCenterPixel[1] - headCenter[1][1])/(tailCenterPixel[0] - headCenter[1][0])
    # else:
    #     k2 = 10000
    # if abs(k0 - k1) < abs(k0 - k2):
    #     headMinPixel = headWholePixel[0][0]
    #     headMaxPixel = headWholePixel[0][1]
    # else:
    #     headMinPixel = headWholePixel[1][0]
    #     headMaxPixel = headWholePixel[1][1]
    arrowPixel = [[[headMinPixel,headMaxPixel],[tailMinPixel,tailMaxPixel]]]   
    return arrowPixel


#### 得到箭头轮廓 ####
def getHeadContours(crop):
    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)

    ##### 设置箭头阈值 #####
    headLowerHsv = np.array([30,30,120])
    headUpperHsv = np.array([120,255,255])
    headMask = cv2.inRange(hsvFrame,headLowerHsv,headUpperHsv)
    # cv2.imshow('headMask',headMask)

    headBlur= cv2.medianBlur(headMask,3)#模糊处理，降低计算量
    headKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    headClose = cv2.morphologyEx(headBlur, cv2.MORPH_CLOSE,headKernel)#闭操作，填充轮廓
    #cv2.imshow('headBlur',headBlur)
    cv2.imshow('headopen',headClose)
    headContours, headHierarchy = cv2.findContours(headClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(crop,headContours,-1,(0,0,255),3)    

    return headContours

#### 得到箭尾轮廓 ####
def getTailContours(crop):
    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)

    ##### 设置箭尾阈值 #####
    tailLowerHsv = np.array([0,120,60])
    tailUpperHsv = np.array([60,255,255])
    tailMask = cv2.inRange(hsvFrame,tailLowerHsv,tailUpperHsv)
    # cv2.imshow('tailMask',tailMask)

    tailBlur = cv2.medianBlur(tailMask,3)
    tailKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    tailOpen = cv2.morphologyEx(tailBlur, cv2.MORPH_OPEN,tailKernel)
    #cv2.imshow('tailBlur',tailBlur)
    cv2.imshow('tailOpen',tailOpen)
    cv2.imshow('crop',crop)
    tailContours, tailHierarchy= cv2.findContours(tailOpen,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    return tailContours       

#### 得到箭头在color——img上的像素坐标 ####     
def getHeadInfo(headContours,cropX,cropY):
    headMinArea = 700
    headWholePixel = []
    headCenter = []
    for i in range(len(headContours)):
        rect = cv2.minAreaRect(headContours[i])
        headArea = cv2.contourArea(headContours[i])
        if headArea > headMinArea:
            headCenter.append([rect[0][0] + cropX,rect[0][1] + cropY])
            box = cv2.boxPoints(rect)
            box = sorted(box,key=lambda s:s[0])
            headMinPixel = [(box[0][0] + box[1][0])/2 + cropX,(box[0][1] + box[1][1])/2 + cropY]
            headMaxPixel = [(box[2][0] + box[3][0])/2 + cropX,(box[2][1] + box[3][1])/2 + cropY]
            headWholePixel.append([headMinPixel,headMaxPixel])
    return headCenter,headWholePixel

#### 得到箭羽在color——img上的像素坐标 ####
def getTailInfo(tailContours,cropX,cropY):
    tailMinArea = 300
    tailWholePixel = []
    tailWholePoint = [] 
    for i in range(len(tailContours)):
        tailArea = cv2.contourArea(tailContours[i])
        if tailArea > tailMinArea:
            for j in range(len(tailContours[i])):
                temp = tailContours[i][j].tolist()
                tailWholePoint.append(temp[0])
            tailWholePoint = sorted(tailWholePoint, key=lambda s: s[0])
            tailMinPixel = [tailWholePoint[0][0] + cropX,tailWholePoint[0][1] + cropY]
            tailMaxPixel = [tailWholePoint[-1][0] + cropX,tailWholePoint[-1][1] + cropY] 
            tailWholePixel.append([tailMinPixel,tailMaxPixel])
            tailWholePoint = []
    return tailWholePixel

#### 过滤掉其他箭的箭羽 ####
def selectTail(tailWholePixel):
    tailCenterPixel = []
    dis = [0,0]
    for i in range(3): #### 计算箭羽中心 ####
        tailCenterPixelX = (tailWholePixel[i][0][0] + tailWholePixel[i][1][0]) / 2
        tailCenterPixelY = (tailWholePixel[i][0][1] + tailWholePixel[i][1][1]) / 2
        tailCenterPixel.append([tailCenterPixelX,tailCenterPixelY])
    for i in range(2): #### 计算距离，按距离分组 ####
        dis[i] = (tailCenterPixel[0][0] - tailCenterPixel[i+1][0]) * (tailCenterPixel[0][0] - tailCenterPixel[i+1][0]) + (tailCenterPixel[0][1] - tailCenterPixel[i+1][1]) * (tailCenterPixel[0][1] - tailCenterPixel[i+1][1])
    if dis[0] < dis[1]:
        tailMinPixel = [(tailWholePixel[0][0][0] + tailWholePixel[1][0][0])/2,(tailWholePixel[0][0][1] + tailWholePixel[1][0][1])/2]
        tailMaxPixel = [(tailWholePixel[0][1][0] + tailWholePixel[1][1][0])/2,(tailWholePixel[0][1][1] + tailWholePixel[1][1][1])/2]
    else:
        tailMinPixel = [(tailWholePixel[0][0][0] + tailWholePixel[2][0][0])/2,(tailWholePixel[0][0][1] + tailWholePixel[2][0][1])/2]
        tailMaxPixel = [(tailWholePixel[0][1][0] + tailWholePixel[2][1][0])/2,(tailWholePixel[0][1][1] + tailWholePixel[2][1][1])/2]
    
    return tailMinPixel,tailMaxPixel

#### 箭尾分组 ####
def classifyTail(tailWholePixel):
    tailCenterPixel = []
    dis = [0,0,0]
    for i in range(4):
        tailCenterPixelX = (tailWholePixel[i][0][0] + tailWholePixel[i][1][0]) / 2
        tailCenterPixelY = (tailWholePixel[i][0][1] + tailWholePixel[i][1][1]) / 2
        tailCenterPixel.append([tailCenterPixelX,tailCenterPixelY])
    for i in range(3):
        dis[i] = (tailCenterPixel[0][0] - tailCenterPixel[i+1][0]) * (tailCenterPixel[0][0] - tailCenterPixel[i+1][0]) + (tailCenterPixel[0][1] - tailCenterPixel[i+1][1]) * (tailCenterPixel[0][1] - tailCenterPixel[i+1][1])
    minDisIndex = dis.index(min(dis))

    #### 第0组和第 minDIsIndex + 1组为一个箭尾
    targetIndex = minDisIndex + 1
    tailSides = [[[0,0],[0,0]],[[0,0],[0,0]]]
    tailSides[0][0][0] = (tailWholePixel[0][0][0] + tailWholePixel[targetIndex][0][0]) / 2
    tailSides[0][0][1] = (tailWholePixel[0][0][1] + tailWholePixel[targetIndex][0][1]) / 2
    tailSides[0][1][0] = (tailWholePixel[0][1][0] + tailWholePixel[targetIndex][1][0]) / 2
    tailSides[0][1][1] = (tailWholePixel[0][1][1] + tailWholePixel[targetIndex][1][1]) / 2
    del tailWholePixel[0]
    del tailWholePixel[targetIndex - 1]
    tailSides[1][0][0] = (tailWholePixel[0][0][0] + tailWholePixel[1][0][0]) / 2
    tailSides[1][0][1] = (tailWholePixel[0][0][1] + tailWholePixel[1][0][1]) / 2
    tailSides[1][1][0] = (tailWholePixel[0][1][0] + tailWholePixel[1][1][0]) / 2
    tailSides[1][1][1] = (tailWholePixel[0][1][1] + tailWholePixel[1][1][1]) / 2

    return tailSides


#### 两个箭头和两个箭尾配对 ####
def classifyArrow(headCenter,headWholePixel,tailSides):
    arrowPixel = []
    threshold = 1
    tailCenter0 = [(tailSides[0][0][0] + tailSides[0][1][0]) / 2,(tailSides[0][0][1] + tailSides[0][1][1]) / 2] 
    tailCenter1 = [(tailSides[1][0][0] + tailSides[1][1][0]) / 2,(tailSides[1][0][1] + tailSides[1][1][1]) / 2] 
    
    if tailSides[0][0][0] != tailSides[0][1][0] :
        k0 = (tailSides[0][0][1] - tailSides[0][1][1]) / (tailSides[0][0][0] - tailSides[0][1][0]) # 箭尾0的斜率
    else:
        k0 = 10000    
    if tailSides[1][0][0] != tailSides[1][1][0] :
        k3 = (tailSides[1][0][1] - tailSides[1][1][1]) / (tailSides[1][0][0] - tailSides[1][1][0]) # 箭尾1的斜率
    else:
        k3 = 10000   
    if tailCenter0[0] != headCenter[0][0]:
        k1 = (tailCenter0[1] - headCenter[0][1]) / (tailCenter0[0] - headCenter[0][0])# 箭头0和箭尾0
    else:
        k1 = 10000
    if tailCenter0[0] != headCenter[1][0]:
        k2 = (tailCenter0[1] - headCenter[1][1]) / (tailCenter0[0] - headCenter[1][0])# 箭头1和箭尾0
    else:
        k2 = 10000

    if abs(k1 - k0) < abs(k2 - k0): #### 00 11组合
        headPixel = headWholePixel[0]
        tailPixel= [tailSides[0][0],tailSides[0][1]]
        arrowPixel.append([headPixel,tailPixel])
        headK = (tailCenter1[1] - headCenter[1][1]) / (tailCenter1[0] - headCenter[1][0])# 箭头1和箭尾1
        if abs(headK - k3) < threshold:
            headPixel = headWholePixel[1]
            tailPixel= [tailSides[1][0],tailSides[1][1]]
            arrowPixel.append([headPixel,tailPixel])
    else: 
        headPixel = headWholePixel[1]
        tailPixel= [tailSides[0][0],tailSides[0][1]]
        arrowPixel.append([headPixel,tailPixel])
        headK = (tailCenter1[1] - headCenter[0][1]) / (tailCenter1[0] - headCenter[0][0])# 箭头0和箭尾1
        if abs(headK - k3) < threshold:
            headPixel = headWholePixel[0]
            tailPixel= [tailSides[1][0],tailSides[1][1]]
            arrowPixel.append([headPixel,tailPixel])

    return arrowPixel 


#### 处理箭头和箭尾的位置，并得到在color_img上的像素坐标 ####
def getArrowInfo(arrowInfo,x,y): 
    arrowCropInfo = []
    arrowCropNum = 0
    for i in range(len(arrowInfo)):
        if arrowInfo[i][0][0][0] > arrowInfo[i][1][1][0]:#### 第i只箭，头尾？，min or max？xy？
            tailPixel = [int(arrowInfo[i][1][0][0]) + x,int(arrowInfo[i][1][0][1]) + y]
            headPixel = [int(arrowInfo[i][0][1][0]) + x,int(arrowInfo[i][0][1][1]) + y]
        elif arrowInfo[i][0][1][0] < arrowInfo[i][1][0][0]:
            tailPixel = [int(arrowInfo[i][1][1][0]) + x,int(arrowInfo[i][1][1][1]) + y]
            headPixel = [int(arrowInfo[i][0][0][0]) + x,int(arrowInfo[i][0][0][1]) + y]
        else:
            # tailPixel = [int(arrowInfo[i][1][1][0]) + x,int(arrowInfo[i][1][1][1]) + y]
            # headPixel = [int(arrowInfo[i][0][0][0]) + x,int(arrowInfo[i][0][0][1]) + y]
            continue
        arrowCropNum = arrowCropNum + 1
        arrowCropInfo.append([headPixel,tailPixel])
    return arrowCropNum, arrowCropInfo
