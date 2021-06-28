import cv2
import pyrealsense2 as rs
import detect
import numpy as np

def getAllContours(crop):
    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)

    ##### 设置箭头阈值 #####
    headLowerHsv = np.array([30,30,120])
    headUpperHsv = np.array([120,255,255])
    headMask = cv2.inRange(hsvFrame,headLowerHsv,headUpperHsv)
    # cv2.imshow('headMask',headMask)
    ##### 设置箭尾阈值 #####
    tailLowerHsv = np.array([0,120,60])
    tailUpperHsv = np.array([60,255,255])
    tailMask = cv2.inRange(hsvFrame,tailLowerHsv,tailUpperHsv)
    # cv2.imshow('tailMask',tailMask)

    headBlur= cv2.medianBlur(headMask,3)#模糊处理，降低计算量
    headKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    headClose = cv2.morphologyEx(headBlur, cv2.MORPH_CLOSE,headKernel)#闭操作，填充轮廓
    #cv2.imshow('headBlur',headBlur)
    cv2.imshow('headopen',headClose)
    #得到箭头轮廓
    headContours, headHierarchy = cv2.findContours(headClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(crop,headContours,-1,(0,0,255),3)    

    tailBlur = cv2.medianBlur(tailMask,3)
    tailKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    tailOpen = cv2.morphologyEx(tailBlur, cv2.MORPH_OPEN,tailKernel)
    # cv2.imshow('tailBlur',tailBlur)
    cv2.imshow('tailOpen',tailOpen)
    cv2.imshow('crop',crop)
    # 得到箭尾轮廓
    tailContours, tailHierarchy= cv2.findContours(tailOpen,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    return headContours,tailContours  

def chooseContours(headContours,tailContours):
    headMinArea = 800
    strCatHeadCont = []
    for i in range(len(headContours)):
        headArea = cv2.contourArea(headContours[i])
        if headArea > headMinArea:
            strCatHeadCont.append(headContours[i])

    strCatTailCont = []
    tailMinArea = 300
    for i in range(len(tailContours)):
        tailArea = cv2.contourArea(tailContours[i])
        if tailArea > tailMinArea:
            strCatTailCont.append(tailContours[i])
    return strCatHeadCont,strCatTailCont



a = detect.detectapi(weights='weights/609.pt')

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)

while 1:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())

    results,names =a.detect([color_image])
    resultsNum = len(results[0][1])
    if resultsNum == 0:# no arrow
        continue
    for i in range(resultsNum):# detect arrow
        result = results[0][1][i]
        m = result[1]
        roi = (m[0] ,m[1] ,m[2]-m[0]  ,m[3]-m[1])
        x, y, w, h = roi
        if x - 25 <= 0:
            x = 0
        else:
            x = x - 25
        if y - 10 <= 0:
            y = 0
        else:
            y = y - 10
        if w + x + 25 >= 639 :
            w = 639 - x
        else:
            w = w + 50
        if h + y + 10 >= 479:
            h = 479 - y
        else:
            h = h + 20

        cv2.imshow("src",color_image)
        src = color_image[y:y+h, x:x + w ]
        crop = src

        headContours,tailContours = getAllContours(crop)
        headDat,tailDat = chooseContours(headContours,tailContours)

        colors = [(0,255,0),(255,0,0),(0,0,255),(255,255,0),(255,0,255),(0,0,255),(0,0,0),(255,255,255)]
        for i in range(len(headDat)):
            cv2.drawContours(crop,headDat[i%8],-1,colors[i],3)
        # cv2.imshow("head",crop)

        for i in range(len(tailDat)):
            cv2.drawContours(crop,tailDat[i],-1,colors[i],3)
        # cv2.imshow("tail",crop)

        k = 1/3
        p = 1/2
        if w/h > 4:
            p = 1
        
        cv2.rectangle(color_image, (x,y), (x + int(w*k),y + int(h*p)), (0,255,0), 4)
        cv2.rectangle(color_image, (x,y + int(h*(1-p) )), (x + int(w*k),y + h), (255,0,0), 4)
        cv2.rectangle(color_image, (x + int(w*(1-k)),y), (x + w,y + int(p*h)), (0,0,255), 4)
        cv2.rectangle(color_image, (x + int(w*(1-k)),y + int(h*(1-p))), (x + w,y + h), (0,0,0), 4)
        cv2.imshow("crop",color_image)

    if cv2.waitKey(1)==ord('q'):
        break
# color_image = cv2.imread("110.jpg")
# color_img = color_image.copy()
# crop = color_image

# headContours,tailContours = getAllContours(crop)
# headDat,tailDat = chooseContours(headContours,tailContours)

# colors = [(0,255,0),(255,0,0),(0,0,255),(255,255,0),(255,0,255),(0,0,255),(0,0,0),(255,255,255)]
# for i in range(len(headDat)):
#     cv2.drawContours(color_image,headDat[i],-1,colors[i],3)
# cv2.imshow("head",color_image)

# for i in range(len(tailDat)):
#     cv2.drawContours(color_img,tailDat[i],-1,colors[i],3)
# cv2.imshow("tail",color_img)

# cv2.waitKey(0)