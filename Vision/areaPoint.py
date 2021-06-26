from logging import DEBUG
import math
from numpy.core.fromnumeric import reshape
import pyrealsense2 as rs
import numpy as np 


#### DEBUG #####
def getPoint(x,y,aligned_depth_frame):
    cameraPoint = []
    depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics 
    dist_to_center = aligned_depth_frame.get_distance(x,y)
    camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin = depth_intrin,pixel = [x,y], depth = dist_to_center)
    cameraPoint = [camera_coordinate[0]*1000,camera_coordinate[1]*1000,camera_coordinate[2]*1000]
    return cameraPoint

def getCoord(cameraPoint):

    transMatrix = np.mat( [[0.5000, -0.6124    ,0.6124,320.24],
 [-0.8660   ,-0.3536    ,0.3536   ,132.9],
 [0   ,-0.7071   ,-0.7071 ,500],
 [ 0,0,0,1]]) 

    standardPoint = np.mat(cameraPoint + [1]).reshape(4,1)
    temp = np.dot(transMatrix,standardPoint)
    temp = np.array(temp)
    coord = [temp[0][0],temp[1][0],temp[2][0]]
    return coord

def getDist(DepthPixel,aligned_depth_frame):
    if DepthPixel[0] < 0:
        DepthPixel[0] = 0
    elif DepthPixel[0] >= 640:
        DepthPixel[0] = 639
    if DepthPixel[1] < 0:
        DepthPixel[1] = 0
    elif DepthPixel[1] > 480:
        DepthPixel[1] = 479
    dist_to_center = aligned_depth_frame.get_distance(DepthPixel[0],DepthPixel[1])

    return dist_to_center


#### BEGIN ####
def transform2camera(allArrowInfo,aligned_depth_frame):
    ##### 获得相机坐标 #####
    arrowCameraCoord = []
    depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics 
    for i in range(len(allArrowInfo)):#### 第i支箭，头尾，xy
        headDepthPixel = [allArrowInfo[i][0][0],allArrowInfo[i][0][1]]
        tailDepthPixel = [allArrowInfo[i][1][0],allArrowInfo[i][1][1]]
        dist_to_center = getDist(headDepthPixel,aligned_depth_frame)
        headPoint = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=headDepthPixel, depth=dist_to_center)
        dist_to_center = getDist(tailDepthPixel,aligned_depth_frame)
        tailPoint = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=tailDepthPixel, depth=dist_to_center)
        arrowCameraCoord.append([[headPoint[0]*1000,headPoint[1]*1000,headPoint[2]*1000],[tailPoint[0]*1000,tailPoint[1]*1000,tailPoint[2]*1000]])   
    return arrowCameraCoord
    

def transform2world(arrowCameraCoord):
    ##### 获得世界坐标 #####
    transMatrix = np.mat( [[ 0.999984859, -2.10667986e-04 ,5.49892993e-03 ,3.17744237e+01],
 [ 1.73828484e-04, 9.99977546e-01 ,6.69901313e-03,-3.22246673e+00],
 [-5.50021773e-03 ,-6.69795583e-03 ,9.99962442e-01, 4.75318982e+00],
 [ 0,0,0,1]])
    transMatrix = np.linalg.inv(transMatrix)

    headCoord = []
    tailCoord = []
    arrowWorldCoord = []
    for i in range(len(arrowCameraCoord)):
        standardCoord = np.mat(arrowCameraCoord[i][0]+[1]).reshape(4,1)
        headCoord = np.dot(transMatrix,standardCoord)
        headCoord = np.array(headCoord)
        standardCoord = np.mat(arrowCameraCoord[i][1]+[1]).reshape(4,1)
        tailCoord = np.dot(transMatrix,standardCoord)
        tailCoord = np.array(tailCoord)
        arrowWorldCoord.append([[headCoord[0],headCoord[1],headCoord[2]],[tailCoord[0],tailCoord[1],tailCoord[2]]])
    return arrowWorldCoord

def completePoint(arrowWorldCoord):
    ##### 初始化特征点 #####
    arrowCarCoord = []
    coeff = 16/59
    targetPoint = [0,0,0]
    slope = 0
#     transMatrix = np.mat( [[0.5000, -0.6124    ,0.6124,320.24],
#  [-0.8660   ,-0.3536    ,0.3536   ,132.9],
#  [0   ,-0.7071   ,-0.7071 ,500],
#  [ 0,0,0,1]]) 

    transMatrix = np.mat( [[1,0,0,0],
 [0,1,0,0],
 [0,0,1,0],
 [ 0,0,0,1]]) 
    headPoint = []
    tailPoint = []
    for i in range(len(arrowWorldCoord)):
        headPoint = arrowWorldCoord[i][0]
        tailPoint = arrowWorldCoord[i][1]

        headPoint = np.matrix(headPoint + [1]).reshape(4,1)
        headPoint = np.dot(transMatrix,headPoint)
        headPoint = np.array(headPoint)
        headPoint = [headPoint[0][0],headPoint[1][0],headPoint[2][0]]

        tailPoint = np.matrix(tailPoint + [1]).reshape(4,1)
        tailPoint = np.dot(transMatrix,tailPoint)
        tailPoint = np.array(tailPoint)
        tailPoint = [tailPoint[0][0],tailPoint[1][0],tailPoint[2][0]]

        arrowCarCoord.append([headPoint,tailPoint])
            
        targetPoint[0] = headPoint[0] + coeff*(tailPoint[0] - headPoint[0])
        targetPoint[1] = headPoint[1] + coeff*(tailPoint[1] - headPoint[1])
        targetPoint[2] = headPoint[2] + coeff*(tailPoint[2] - headPoint[2])

        slope = math.atan((headPoint[1] - tailPoint[1])/(headPoint[0] - tailPoint[0]))*180 / math.pi

        print("slope",slope)
        # print("headPoint",headPoint)
        # print("tailPoint",tailPoint)
        # print("targetPoint",targetPoint)

    print("process Done")

    return arrowCarCoord
    #return sendPoint,slope


