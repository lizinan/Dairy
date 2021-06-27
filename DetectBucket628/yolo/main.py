import pyrealsense2 as rs
import numpy as np
import cv2
import detect

import mySerial as ms
import calibrate as cali
import completePoint as cp  
import processImg as proc

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
    # cv2.imshow('RealSense', color_image)
    results,names =a.detect([color_image])

    # no arrow
    if results[0][1] == []:
        continue

    # arrow
    for result in results[0][1]:
        # get crop image location
        m = result[1]
        roi = (m[0],m[1],m[2]-m[0] + 1,m[3]-m[1] + 1)
        x, y, w, h = roi

        # image process
        maxBox,centerPoint = proc.process(results,x,y,w,h)

        # get camera coordinate
        prepoint = cp.getPoint(maxBox,centerPoint,aligned_depth_frame,x,y)
        correctPoint,slope = cp.completePoint(prepoint)
        if slope < 0:
            slope = slope + 180
        print(correctPoint)
        print(slope)

        # get world coordinate
        # world_coordinate = cali.transform2world(point)

    # send message
    ms.sendMsg(mySerial,msgId)

pipeline.stop()
