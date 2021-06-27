import pyrealsense2 as rs
import numpy as np
import cv2
import detect
import threading

import mySerial as ms
import calibrate as cali
import completePoint as cp  

global sendCount

sendCount = 0
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)

align_to = rs.stream.color
align = rs.align(align_to)

a = detect.detectapi(weights='weights/426.pt')

# TODO: 让realsense只返回一半的图像，把轮廓检测改一波
msT = threading.Thread(target=ms.recMsg())
msT.start()

# openSerial
while 1:
    frames = pipeline.wait_for_frames()
    
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()

    color_image = np.asanyarray(color_frame.get_data())
    cv2.imshow('RealSense', color_image)

    if cv2.waitKey(1)==ord('q'):
       break

    results,names =a.detect([color_image])
    img = results[0][0] #第一张图片的处理结果图片

    if results[0][1] == []:
        continue
    
    for result in results[0][1]:
        m = result[1]
        roi = (m[0],m[1],m[2]-m[0] + 1,m[3]-m[1] + 1)
        x, y, w, h = roi

        crop = img[y:y+h, x:x+w]
        src = crop
        hsvFrame = cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
        #cv2.imshow('hsvFrame',hsvFrame)

        lowerHSV = np.array([0,0,0])
        upperHSV = np.array([180,120,110])
        mask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)
        #cv2.imshow('inRange',mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
        #cv2.imshow('open',binary)

        canny = cv2.Canny(binary, 50, 150)
        #cv2.imshow('canny',canny)

        contours, hierarchy = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

        cv2.drawContours(src,contours,-1,(0,0,255),3)  
        
        #cv2.imshow("img", src) 
        print("process ends") 

        maxArea = 0
        maxBox = 0
        for cont in contours:
            # 对每个轮廓点求最小外接矩形
            rect = cv2.minAreaRect(cont)
            # cv2.boxPoints可以将轮廓点转换为四个角点坐标
            box = cv2.boxPoints(rect)
            area = cv2.contourArea(box)
            # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
            startidx = box.sum(axis=1).argmin()
            box = np.roll(box,4-startidx,0)
            # 在原图上画出预测的外接矩形
            box = box.reshape((-1,1,2)).astype(np.int32)
            if area > maxArea:
                maxArea = area
                maxBox = box
            i = 0
            while i<4:
                if maxBox[i][0][0] < 0:
                    maxBox[i][0][0] = 0
                if maxBox[i][0][1] < 0:
                    maxBox[i][0][1] = 0
                if maxBox[i][0][0] > w -1:
                    maxBox[i][0][0] = w - 1
                if maxBox[i][0][1] > h - 1:
                    maxBox[i][0][1] = h - 1 
                i = i+1  
                                 
                #print(box,"box")
            fit = cv2.polylines(src,[maxBox],True,(0,255,0),1)
            cv2.imshow('test',fit)
            depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
            i = 0
            x1 = 0
            y1 = 0
            r2 = 0
            point = ([0,0],[0,0],[0,0],[0,0])
            rux = 0
            for rect_point in maxBox:
                depth_pixel = [x + rect_point[0][0] - 1,y + rect_point[0][1] - 1]
                dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
                #print("aligned_depth",dist_to_center * 1000)
                #camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=depth_pixel, depth=dist_to_center)
                #print(camera_coordinate,"camera_coordinate")
                x1 = (depth_pixel[0] - depth_intrin.ppx)/depth_intrin.fx
                y1 = (depth_pixel[1] - depth_intrin.ppy)/depth_intrin.fy
                r2  = x1*x1 + y1*y1
                f = 1 + depth_intrin.coeffs[0]*r2 + depth_intrin.coeffs[1]*r2*r2 + depth_intrin.coeffs[4]*r2*r2*r2
                ux = x1*f + 2*depth_intrin.coeffs[2]*x1*y1 + depth_intrin.coeffs[3]*(r2 + 2*x1*x1)
                if dist_to_center == 0:
                    rux = ux
                point[i][0]= ux*dist_to_center*1000
                point[i][1]= dist_to_center*1000
                i = i + 1
            n,point = cp.completePoint(point,rux)
            #if point != None:
                #world_coordinate = cali.transform2world(point)
    ms.sendMsg(point)
pipeline.stop()

