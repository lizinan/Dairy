import pyrealsense2 as rs
import numpy as np
import cv2

import SerialPort as sp
import aPoint as ap  
import imgProcess as proc
import time

mySerial = sp.openSerial()

# open realsense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)

#### decide player #### ####这个地方判断有点难顶，可能需要手动
# frames = pipeline.wait_for_frames()
# color_frame = frames.get_color_frame()
# color_image = np.asanyarray(color_frame.get_data())
# player = proc.decidePlayer(color_image)
player = 0
carX = -1040
carY = 150
while True:
    t0 = time.time()
    # see realsense color pic
    if cv2.waitKey(1)==ord('q'):
        break

    #### get color_img, depth_img ####
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame() 
    color_image = np.asanyarray(color_frame.get_data())
    cv2.imshow('RealSense', color_image)

    #### 参数初始化 ####
    w = 640
    h = 480
    redPixels = [0,0]
    bluePixels = [0,0]
    bucketInfo = [0,0]

    #### 裁剪ROI ####s
    cropNear = color_image[int(h/3):int(h*2/3),350:540]
    cropFar = color_image[190:290,140:270]
    crops = [cropNear,cropFar]
    cropLocation = [350,int(h/3),140,190]

    for i in range(2): #### 一张图片里有两组桶 ####
        redPixels[i],bluePixels[i],redFlag,blueFlag,bucket = proc.process(crops[i],cropLocation[2*i],cropLocation[2*i + 1],i)

        if bucket == 0: #### 没有识别到桶，将角度记为0 ####
            redAngle = 0
            blueAngle = 0
            bucketInfo[i] = [-1,-1] 

        elif bucket == 1: #### 桶被遮挡 #####

            if redFlag == 1: #### 红桶是近端 ####
                cv2.circle(color_image,(round(redPixels[i][0]),round(redPixels[i][1])),5,(0,255,255),1)

                #### 从像素坐标系换算q到相机坐标系，再换算到參盘坐标系 ####
                redPoint = ap.getPoint(redPixels[i],aligned_depth_frame)
                redCoord = ap.transform2world(redPoint) 
                redTableCoord = ap.transform2Car(redCoord)

                if player == 0: #### 玩家为红方，直接得斜率
                    redAngle = ap.getAngle(redTableCoord)
                    bucketInfo[i] = [redAngle,redFlag]

                else: #### 蓝方，需要补全被遮挡的桶
                    redOriginCoord = ap.transform2Origin(redTableCoord)
                    redOriginAngle = ap.getAngle(redOriginCoord)
                    blueAngle = ap.completeBucket(redOriginAngle,carX,carY)
                    bucketInfo[i] = [blueAngle,blueFlag]

            if blueFlag == 1:
                cv2.circle(color_image,[round(bluePixels[i][0]),round(bluePixels[i][1])],5,(0,255,255),1)
                bluePoint = ap.getPoint(bluePixels[i],aligned_depth_frame)
                blueCoord = ap.transform2world(bluePoint) 
                blueTableCoord = ap.transform2Car(blueCoord)

                if player == 0:
                    blueOriginCoord = ap.transform2Origin(blueTableCoord)
                    blueOriginAngle = ap.getAngle(blueOriginCoord)
                    redAngle = ap.completeBucket(blueOriginAngle,carX,carY)
                    bucketInfo[i] = [redAngle,redFlag]

                else:
                    blueAngle = ap.getAngle(blueTableCoord)
                    bucketInfo[i] = [blueAngle,blueFlag]

        else:
            cv2.circle(color_image,(round(redPixels[i][0]),round(redPixels[i][1])),5,(0,0,255),1)
            cv2.circle(color_image,[round(bluePixels[i][0]),round(bluePixels[i][1])],5,(0,0,255),1)

            if player == 0:
                redPoint = ap.getPoint(redPixels[i],aligned_depth_frame)
                redCoord = ap.transform2world(redPoint) 
                redTableCoord = ap.transform2Car(redCoord)
                redAngle = ap.getAngle(redTableCoord)
                bucketInfo[i] = [redAngle,redFlag]

            else: 
                bluePoint = ap.getPoint(bluePixels[i],aligned_depth_frame)
                blueCoord = ap.transform2world(bluePoint) 
                blueTableCoord = ap.transform2Car(blueCoord)
                blueAngle = ap.getAngle(blueTableCoord)
                bucketInfo[i] = [blueAngle,blueFlag]
    
    #### DEBUG ####
    cv2.imshow("showBucket",color_image)
    print("bucketInfo",bucketInfo)
    print("fps:",1/(time.time()- t0))
    #### send message ####
    if mySerial != None:
        msgId = sp.recMsg(mySerial)
        sp.sendMsg(mySerial,msgId,bucketInfo)

pipeline.stop()
