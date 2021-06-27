import cv2
import detect
import numpy as np

cap=cv2.VideoCapture(4)
a=detect.detectapi(weights='weights/arrowtest.pt')
while True:
    rec,img = cap.read()

    result,names =a.detect([img])
    img=result[0][0] #第一张图片的处理结果图片
    cv2.imshow("video",img)
    print("hhh")
    print(result[0][1])

    if cv2.waitKey(1)==ord('q'):
        break
    
    if result[0][1] == []:
        continue
    else:
        m = result[0][1][0][1]
        roi = (m[0],m[1],m[2]-m[0]+1,m[3]-m[1]+1)
        x, y, w, h = roi

        crop = img[y:y+h, x:x+w]
        cv2.imshow('crop', crop)
        cv2.imwrite('crop.jpg', crop)

        src = cv2.imread('crop.jpg')
        hsvFrame = cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
        cv2.imshow('hsvFrame',hsvFrame)

        lowerHSV = np.array([0,0,0])
        upperHSV = np.array([180,120,110])
        mask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)
        cv2.imshow('inRange',mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
        cv2.imshow('open',binary)

        canny = cv2.Canny(binary, 50, 150)
        cv2.imshow('canny',canny)

        contours, hierarchy = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

        cv2.drawContours(src,contours,-1,(0,0,255),3)  
        
        cv2.imshow("img", src)  

        maxArea = 0
        maxBox = 0
        for cont in contours:
            # 对每个轮廓点求最小外接矩形
            rect = cv2.minAreaRect(cont)
            # cv2.boxPoints可以将轮廓点转换为四个角点坐标
            box = cv2.boxPoints(rect)
            # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
            startidx = box.sum(axis=1).argmin()
            box = np.roll(box,4-startidx,0)
            # 在原图上画出预测的外接矩形
            box = box.reshape((-1,1,2)).astype(np.int32)
            area = cv2.contourArea(box)
            if area > maxArea:
                maxArea = area
                maxBox = box
            print(area)
        print(maxBox)
        img = cv2.polylines(src,[maxBox],True,(0,255,0),1)
        cv2.imshow('test',img)

print("process ends")

