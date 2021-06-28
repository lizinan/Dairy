import cv2
import pyrealsense2 as rs
import numpy as np


#### 读取一张realsense的图像
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)

i = 0
n = 90
while i < n:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())
    i = i + 1
    if i == n:
        cv2.imwrite('%d.jpg'%i,color_image)
  
###########创建hsv滚动条
def nothing(x):
    pass
cv2.namedWindow("Tracking")
cv2.createTrackbar("LH","Tracking",35,255,nothing)
cv2.createTrackbar("LS","Tracking",43,255,nothing)
cv2.createTrackbar("LV","Tracking",46,255,nothing)
cv2.createTrackbar("UH","Tracking",77,255,nothing)
cv2.createTrackbar("US","Tracking",255,255,nothing)
cv2.createTrackbar("UV","Tracking",255,255,nothing)

###显示hsv滤波后的图片
while True:
    frame = cv2.imread('%d.jpg'%i)
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    l_h = cv2.getTrackbarPos("LH","Tracking")
    l_s = cv2.getTrackbarPos("LS","Tracking")
    l_v = cv2.getTrackbarPos("LV","Tracking")
    
    u_h = cv2.getTrackbarPos("UH","Tracking")
    u_s = cv2.getTrackbarPos("US","Tracking")
    u_v = cv2.getTrackbarPos("UV","Tracking")
    
    
    l_g = np.array([l_h, l_s, l_v]) # lower green value
    u_g = np.array([u_h,u_s,u_v])

    mask = cv2.inRange(hsv,l_g,u_g)
    
    res=cv2.bitwise_and(frame,frame,mask=mask) # src1,src2
     
    cv2.imshow("frame", frame)
    cv2.imshow("mask", mask)
    cv2.imshow("res", res)
    key = cv2.waitKey(1)
    if key == 27: # Esc
        break

cv2.destroyAllWindows()