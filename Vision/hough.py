import cv2
import numpy as np
import pyrealsense2 as rs
import time
import detect
 
#两个回调函数
def HoughLinesP(minLineLength):
    tempIamge = src.copy()
    lines = cv2.HoughLinesP( edges, 1, np.pi/180,threshold=minLineLength,minLineLength=260,maxLineGap=30)
    for x1,y1,x2,y2 in lines[:,0]:
        cv2.line(tempIamge,(x1,y1),(x2,y2),(0,255,0),2)
    print("lineInfo",lines)
    cv2.imshow(window_name,tempIamge)

def HoughLines(minLineLength):
    tempIamge = src.copy()
    lines = cv2.HoughLines( edges, 1, np.pi/180,0)
    for x1,y1,x2,y2 in lines[:,0]:
        cv2.line(tempIamge,(x1,y1),(x2,y2),(0,255,0),2)
    print("lineInfo",lines)
    cv2.imshow(window_name,tempIamge)

#临时变量
minLineLength = 50
 
#全局变量
# minLINELENGTH = 20
window_name = "HoughLines Demo"
 
 
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)


a = detect.detectapi(weights='weights/609.pt')#609

#读入图片，模式为灰度图，创建窗口
while True:
    t1 = time.time()
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())
    t2 = time.time()
    print("realsense fps",1/(t2-t1))


    results,names =a.detect([color_image])
    if results[0][1] == []:
        continue
    result = results[0][1][0]
    m = result[1]
    roi = (m[0] ,m[1] ,m[2]-m[0]  ,m[3]-m[1])
    x, y, w, h = roi
    if x - 25 <= 0:
        x = 0
    else:
        x = x - 25
    if y - 25 <= 0:
        y = 0
    else:
        y = y - 25
    if w + x + 25 >= 639 :
        w = 639 - x
    else:
        w = w + 50
    if h + y + 25 >= 479:
        h = 479 - y
    else:
        h = h + 50

    #src = color_image[y:y+100, x + 400:x + w ]
    src = color_image[y:y+h,x:x+w]
    cv2.imshow("a",color_image)
    print("running")
    try:
        gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(gray,(3,3),0)
        edges = cv2.Canny(img, 50, 150, apertureSize = 3)
        cv2.namedWindow(window_name)
        
        #初始化
        HoughLinesP(minLineLength)
    except:
        pass

    t3 = time.time()
    print("fps",1/(t3-t1))
    cv2.waitKey(10)