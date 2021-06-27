import numpy as np
import cv2

def process(results,x,y,w,h):
    img = results[0][0]
    crop = img[y:y+h, x:x+w]
    cv2.imshow('crop',crop)

    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
    cv2.imshow('hsvFrame',hsvFrame)

    lowerHSV = np.array([0,0,0])
    upperHSV = np.array([180,130,105])
    mask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)
    cv2.imshow('inRange',mask)

    blur = cv2.medianBlur(mask,3)
    cv2.imshow('blur',blur)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    binary = cv2.morphologyEx(blur, cv2.MORPH_OPEN,kernel)
    cv2.imshow('open',binary)

    canny = cv2.Canny(binary, 50, 150)
    cv2.imshow('canny',canny)

    contours, hierarchy = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  
    #print("contours",contours)

    cv2.drawContours(crop,contours,-1,(0,0,255),3)  
    
    maxArea = 0
    maxBox = 0
    for cont in contours:
        # 对每个轮廓点求最小外接矩形
        rect = cv2.minAreaRect(cont)
        # cv2.boxPoints可以将轮廓点转换为四个角点坐标
        box = cv2.boxPoints(rect)
        area = cv2.contourArea(box)
        # # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
        startidx = box.sum(axis=1).argmin()
        box = np.roll(box,4-startidx,0)
        # 在原图上画出预测的外接矩形
        box = box.reshape((-1,1,2)).astype(np.int32)
        if area > maxArea:
            maxArea = area
            maxCont = cont
            maxBox = box

    for i in range(4):
        if maxBox[i][0][0] < 0:
            maxBox[i][0][0] = 0
        if maxBox[i][0][1] < 0:
            maxBox[i][0][1] = 0
        if maxBox[i][0][0] > w -1:
            maxBox[i][0][0] = w - 1
        if maxBox[i][0][1] > h - 1:
            maxBox[i][0][1] = h - 1 
                                
    fit = cv2.polylines(crop,[maxBox],True,(0,255,0),1)
    #print("maxbox",maxBox)
    cv2.imshow('detect arrow',fit)

        # #cv2.imshow("img", crop) 
        # print("process successs") 
    return maxBox