import pyrealsense2 as rs
import numpy as np
import cv2
import detect

import mySerial as ms
import calibrate as cali
import areaPoint as cp  
import area as proc

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
a = detect.detectapi(weights='weights/426.pt')

while True:
    # receive message
    msgId = ms.recMsg(mySerial)

    # test
    if cv2.waitKey(1)==ord('q'):
        break

    # get color_img, depth_img
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame() 

    # yolo detect
    color_image = np.asanyarray(color_frame.get_data())
    
    
    cv2.imshow('RealSense', color_image)
    results,names =a.detect([color_image])

    # no arrow
    if results[0][1] == []:
        continue

    # arrow
    # for result in results[0][1]:
    #     # get crop image location
    #     m = result[1]
    #     roi = (m[0],m[1],m[2]-m[0] + 1,m[3]-m[1] + 1)
    #     x, y, w, h = roi

    #     # image process
    #     maxCont = proc.process(results,x,y,w,h)

    #     # get camera coordinate
    #     prepoint = cp.getPoint(maxCont,aligned_depth_frame,x,y)
    #     world_coordinate = cp.transform2world(prepoint)
    #     centerPoint,slope = cp.completePoint(world_coordinate)
    #     print(centerPoint)
    #     print(slope)

    #     # get world coordinate
    #     #world_coordinate = cp.transform2world(prepoint)
    #     #world_coordinate = cali.transform2world(centerPoint)

    # get crop image location
    result = results[0][1][0]
    m = result[1]
    roi = (m[0],m[1],m[2]-m[0] + 1,m[3]-m[1] + 1)
    x, y, w, h = roi

    # image process
    maxBox = proc.process(results,x,y,w,h)

    # get camera coordinate
    prepoint = cp.getPoint(maxBox,aligned_depth_frame,x,y)
    world_coordinate = cp.transform2world(prepoint)
    centerPoint,slope = cp.completePoint(world_coordinate)
    print(centerPoint)
    print(slope)

    # get world coordinate
    #world_coordinate = cp.transform2world(prepoint)
    #world_coordinate = cali.transform2world(centerPoint)

    # send message
    ms.sendMsg(mySerial,msgId)

pipeline.stop()
