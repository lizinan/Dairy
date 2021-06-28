import math
import pyrealsense2 as rs
import numpy as np 


def getCameraPoint(Pixel,aligned_depth_frame):
    Point = []
    depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics 
    dist_to_center = aligned_depth_frame.get_distance(round(Pixel[0]),round(Pixel[1]))
    camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=Pixel, depth=dist_to_center)
    Point = [camera_coordinate[0]*1000,camera_coordinate[1]*1000,camera_coordinate[2]*1000]
    return Point
    
def transform2world(point):
    #realsense1
    # t_matrix = np.mat([22.243631,-162.49173,9.1566334])
    # r_matrix = np.mat([[0.99977434, -0.0082152346, 0.019591497],[0.0077725407, 0.99971515, 0.022566302],[-0.019771304, -0.022408932, 0.99955338]])

    transMatrix = np.mat( [[ 0.999984859, -2.10667986e-04 ,5.49892993e-03 ,3.17744237e+01],
 [ 1.73828484e-04, 9.99977546e-01 ,6.69901313e-03,-3.22246673e+00],
 [-5.50021773e-03 ,-6.69795583e-03 ,9.99962442e-01, 4.75318982e+00],
 [ 0,0,0,1]])
    transMatrix = np.linalg.inv(transMatrix)

    coord = []
    standardCoord = np.mat(point+[1]).reshape(4,1)
    coord = np.dot(transMatrix,standardCoord)
    coord = np.array(coord)

    return coord


def transform2Table(coord):
#     transMatrix = np.mat( [[ 0.5, -0.8660254037844386,0,117.4494],
#  [0,0,-1,-350.8013],
#  [0.8660254037844386,0.5,0,550],
#  [ 0,0,0,1]])
    transMatrix = np.mat( [[ 0.5, 0.8660254037844386,0,-117.4494],
 [0,0,-1,-350.8013],
 [-0.8660254037844386,0.5,0,-550],
 [ 0,0,0,1]])
    transMatrix = np.linalg.inv(transMatrix)

    carCoord = []
    standardCoord = np.mat(coord).reshape(4,1)
    coord = np.dot(transMatrix,standardCoord)
    carCoord = np.array(coord)
    return carCoord

# def transform2Origin(coord):
#     transMatrix = np.mat( [[ 1,0,0 ,-10400 ],
#  [0,1,0,-1500],
#  [0,0,1,0],
#  [ 0,0,0,1]])
#     transMatrix = np.linalg.inv(transMatrix)
#     standardCoord = np.mat(coord ).reshape(4,1)
#     coord = np.dot(transMatrix,standardCoord)
#     coord = np.array(coord)
#     return coord

def getAngle(coord):
    Angle = coord[1]/coord[0]
    Angle = math.atan(Angle)
    Angle = Angle*180/math.pi
    return Angle

def completeBucket(Angle,carX,carY,n):
    targetAngle = 0
    k = math.tan(Angle*math.pi/180)
    A = k*k + 1
    if n == 0:
        B = (-2)*(5950 + 10400*k*k + 1950*k)
        C = 5950*5950 + (10400*k + 1950)*(10400*k + 1950) - 350*350
        try:
            delta = math.sqrt(B*B - 4*A*C)
            x = (-B + delta) / (2 * A)
            y = k*(x - 10400) + 1500
            targetX = 2*5950 - x
            targetY = 2*3450 - y
        except:
            targetX = 0
            targetY = 0
    else:
        B = (-2)*(5950 + 10400*k*k + 4450*k) 
        C = 5950*5950 + (10400*k + 4450)*(10400*k + 4450) - 350*350
        try:
            delta = math.sqrt(B*B - 4*A*C)
            x = (-B + delta) / (2 * A)
            y = k*(x - 10400) + 1500
            targetX = 2*5950 - x
            targetY = 2*5950 - y  
        except:
            targetX = 0
            targetY = 0

    targetAngle = math.atan((targetY- carY)/(targetX - carX))
    targetAngle = targetAngle*180/math.pi
    return targetAngle