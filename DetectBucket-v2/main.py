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

player = 0
carX = 10400
carY = 1500

while True:
    t0 = time.time()
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
    bucketInfo = [0,0]
    correction = [3,4.8]
    correction1 = [3,3]

    #### 裁剪ROI ####s
    cropLocation = [[160,220,290,320],[400,200,540,280]]

    for i in range(2): #### 一张图片里有两组桶 ####
        pixels,states = proc.process(color_image,cropLocation[i],i)

        try:
            cv2.circle(color_image,(round(pixels[0][0]),round(pixels[0][1])),5,(0,255,255),1)
        except:
            pass
        try:
            cv2.circle(color_image,[round(pixels[1][0]),round(pixels[1][1])],5,(0,255,255),1)
        except:
            pass

        if states[0] == 0 and states[1] == 0: #### 没有识别到桶 ####
            bucketInfo[i] = [-1,-1] 
        else:#### 识别到桶 ####
            if states[player] == 1:#### 如果我方桶没有被遮挡 ####
                cameraPoint = ap.getCameraPoint(pixels[player],aligned_depth_frame)
                worldCoord = ap.transform2world(cameraPoint)
                tableCoord = ap.transform2Table(worldCoord)
                targetAngle = ap.getAngle(tableCoord)#### 直接算出桶相对盘的斜率 ####
                print("Angle1",targetAngle)
                targetAngle = targetAngle - correction[i] #### 计算补偿量 ####
                print("Angle2",targetAngle)

            else: #### 桶被遮挡，间接算斜率####
                print("pixle",pixels[1- player])
                cameraPoint = ap.getCameraPoint(pixels[1 - player],aligned_depth_frame)
                worldCoord = ap.transform2world(cameraPoint)
                tableCoord = ap.transform2Table(worldCoord)
                angle = ap.getAngle(tableCoord) #### 补偿量 ####
                print("Angle",angle - correction[i])

                targetAngle = ap.completeBucket(angle - correction[i],carX,carY,i)#### 根据车在世界坐标系下位置解算目标桶斜率 ####
                targetAngle = targetAngle  - correction1[i]#### 计算补偿量 ####

            bucketInfo[i] = [targetAngle,states[player]]
    
    #### DEBUG ####
    cv2.imshow("showBucket",color_image)
    print("bucketInfo",bucketInfo)
    print("fps:",1/(time.time()- t0))

    #### 通信 ####
    if mySerial != None:
        msgId = sp.recMsg(mySerial)
        if msgId == 3:
            carX,carY = sp.getCarPos(mySerial)
            player = proc.decidePlayer(color_image)
        else:
            sp.sendMsg(mySerial,msgId,bucketInfo)

pipeline.stop()
