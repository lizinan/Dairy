import cv2
import pyrealsense2 as rs
import numpy as np

img = cv2.imread("100.jpg")
cv2.imshow("img", img)
# 转换为灰度图像
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hu=cv2.HuMoments(cv2.moments(img_gray)).flatten()
print(hu)

def getContours(color_image):
    hsvFrame = cv2.cvtColor(color_image,cv2.COLOR_BGR2HSV)

    ##### 设置箭头阈值 #####
    headLowerHsv = np.array([30,30,120])
    headUpperHsv = np.array([120,255,255])
    headMask = cv2.inRange(hsvFrame,headLowerHsv,headUpperHsv)
    # cv2.imshow('headMask',headMask)
    ##### 设置箭尾阈值 #####
    tailLowerHsv = np.array([15,90,90])
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
    #cv2.imshow('tailBlur',tailBlur)
    cv2.imshow('tailOpen',tailOpen)
    cv2.imshow('crop',color_image)
    # 得到箭尾轮廓
    tailContours, tailHierarchy= cv2.findContours(tailOpen,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    return headContours,tailContours  

headContours,tailContours = getContours(img)
img=cv2.drawContours(img,headContours[0],-1,(0,255,0),5)
img=cv2.drawContours(img,tailContours[0],-1,(0,255,0),5)
cv2.imshow("img",img)
cv2.waitKey(0)


pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)

while 1:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())

    head,tail = getContours(color_image)
    if head == [] or tail == []:
        print("running")
        continue
    ret1 = cv2.matchShapes(headContours[1], head[0], 1, 0.0)
    ret2 = cv2.matchShapes(tailContours[0], tail[0], 1, 0.0)
    if ret1 < 500 and ret2 < 500:
        cv2.drawContours(color_image,head[0],-1,(255,0,0),3)
        cv2.drawContours(color_image,tail[0],-1,(0,0,255),3)
        tailTemp = cv2.moments(tail,True)
        mc = (int(tailTemp['m10']/tailTemp['m00']),int(tailTemp['m01']/tailTemp['m00']))
        cv2.circle(color_image, mc, 1, (0, 255, 0), -1) #负数表示绘制同心圆
        headTemp = cv2.moments(head,True)
        mc = (int(headTemp['m10']/headTemp['m00']),int(headTemp['m01']/headTemp['m00']))
        cv2.circle(color_image, mc, 1, (0, 255, 0), -1) #负数表示绘制同心圆
        cv2.imshow("result",color_image)
    if cv2.waitKey(1)==ord('q'):
        cv2.destroyAllWindows()
        break
    print("head",ret1)
    print("tail",ret2)