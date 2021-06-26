import pyrealsense2 as rs
import numpy as np
import cv2
import detect

import SerialPort as ms
import areaPoint as cp  
import area as proc
import time

# open serial
mySerial = ms.openSerial()

# open realsense
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)

# choose yolo weights
a = detect.detectapi(weights='weights/609.pt')

def getposHsv(event, x, y, flags, param):
    if event==cv2.EVENT_LBUTTONDOWN:
        miceCamerapoint = []
        miceWorldpoint = []
        miceCamerapoint = cp.getPoint(x,y,aligned_depth_frame)
        print("x,y:",x,y)
        print("miceCamera",miceCamerapoint)
        miceWorldpoint = cp.getCoord(miceCamerapoint)
        print("miceCoord",miceWorldpoint)


while True:
    if cv2.waitKey(1)==ord('q'):
        break

    t1 = time.time()
    # get color_img, depth_img
    frames = pipeline.wait_for_frames()
    # depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame() 
    color_image = np.asanyarray(color_frame.get_data())
    cv2.imshow('RealSense', color_image)
    t2 = time.time()

    # print("aligned time consume:",t2 - t1)
    # debug
    cv2.imshow("drawing",color_image)
    cv2.setMouseCallback("drawing", getposHsv,color_image)

    # yolo detect
    results,names =a.detect([color_image])
    # scan results
    resultsNum = len(results[0][1])
    # print("Yolo:",resultsNum)
    t3 = time.time()
    # print("Yolo Consume:",t3 - t2)
    # get crop image location and dilact
    if resultsNum == 0:# no arrow
        continue
    allArrowInfo = []
    arrow = []
    for i in range(resultsNum):# detect arrow
        result = results[0][1][i][1]
        x = result[0]
        y = result[1]
        w = result[2] - result[0]
        h = result[3] - result[1]
        if x - 25 <= 0:
            x = 0
        else:
            x = x - 25
        if y - 10 <= 0:
            y = 0
        else:
            y = y - 10
        if w + x + 25 >= 639:
            w = 639 - x
        else:
            w = w + 50
        if h + y + 10 >= 479:
            h = 479 - y
        else:
            h = h + 20

        # get arrow Image Info
        arrowCropNum,arrowInfo = proc.process(color_image,x,y,w,h)### 一只箭和两只箭分开！！！！！！！！！返回整张图片的坐标

        allArrowInfo = arrowInfo + allArrowInfo

    t4 = time.time()
    # print("processDat consume:",t4 - t3)
    #### DEBUG #####     #圈圈
    colors = [(0,255,0),(255,0,0),(0,0,255),(255,255,0),(255,0,255),(0,0,255),(0,0,0),(255,255,255)]
    for i in range(len(allArrowInfo)):
        cv2.circle(color_image,allArrowInfo[i][0],5,colors[i],0)
        cv2.circle(color_image,allArrowInfo[i][1],5,colors[i+1],0)
    print("Arrow num:",len(allArrowInfo))
    cv2.imshow("drawcircle",color_image)

    print("allArrowInfo",allArrowInfo)

    # # transform coordinate
    arrowCameraCoord = cp.transform2camera(allArrowInfo,aligned_depth_frame)
    arrowWorldCoord = cp.transform2world(arrowCameraCoord)
    arrowCarCoord = cp.completePoint(arrowWorldCoord)
    print("arrowCameraCoord",arrowCameraCoord)
    print("arrowWorldCoord",arrowWorldCoord)
    print("arrowCarCoord",arrowCarCoord)
    # print("total Consume",time.time() - t1)
    #send message
    if mySerial != None:
        msgId = ms.recMsg(mySerial)
        ms.sendMsg(mySerial,msgId,arrowCarCoord)

pipeline.stop()