import math
import pyrealsense2 as rs
import numpy as np 

def getAngle(coord):
    Angle = coord[1]/coord[0]
    Angle = math.atan(Angle)
    Angle = Angle*180/math.pi
    return Angle


def completeBucket(Angle,carX,carY):
    targetAngle = 0
    k = math.tan(Angle)
    A = k*k + 1
    B = 2*(595 - 345*k)
    C = 471825 #595*595 + 345*345 - 35*35
    try:
        delta = math.sqrt(B*B - 4*A*C)
        x = (-B - delta) / (2 * A)
        y = k*x
        targetX = 2*(-595) - x
        targetY = 2*345 - y

        coord = [targetX,0,targetY,1]
        transMatrix = np.mat( [[ 0,0,0 ,-1040 ],
        [0,0,0,450],
        [0,0,0,0],
        [ 0,0,0,1]])
        transMatrix = np.linalg.inv(transMatrix)
        carCoord = []
        standardCoord = np.mat(coord).reshape(4,1)
        coord = np.dot(transMatrix,standardCoord)
        carCoord = np.array(coord)

        targetAngle = math.atan((carCoord[1]- carY)/(carCoord[0] - carX))
        targetAngle = targetAngle*180/math.pi
    except: 
        pass
    return targetAngle


def getPoint(Pixel,aligned_depth_frame):
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


def transform2Car(coord):
    transMatrix = np.mat( [[ 0.5, -0.8660254037844386,0,117.4494],
 [0,0,-1,-350.8013],
 [0.8660254037844386,0.5,0,550],
 [ 0,0,0,1]])
    transMatrix = np.linalg.inv(transMatrix)

    carCoord = []
    standardCoord = np.mat(coord+[1]).reshape(4,1)
    coord = np.dot(transMatrix,standardCoord)
    carCoord = np.array(coord)
    return carCoord

def transform2Origin(coord):
    transMatrix = np.mat( [[ 0,0,0 ,-1040 ],
 [0,0,0,450],
 [0,0,0,0],
 [ 0,0,0,1]])
    standardCoord = np.mat(coord).reshape(4,1)
    coord = np.dot(transMatrix,standardCoord)
    coord = np.array(coord)
    return coord

def completePoint(world_coordinate):
    bucketPoint = [0,0,0,0]
    slope = [0,0,0,0]
    bucketPoint[0] = world_coordinate[0]
    bucketPoint[1] = world_coordinate[1]
    world_coordinate = sorted(world_coordinate, key=lambda s: s[0], reverse=True) 
    bucketPoint[2] = world_coordinate[1]
    bucketPoint[3] = world_coordinate[0]
    # print("bucket",bucketPoint)

    for i in range(len(bucketPoint)):
        slope[i] = abs(math.atan(bucketPoint[i][1]/bucketPoint[i][0])*180/math.pi)

    print(bucketPoint)
    
    print(slope)
    return slope

    # slope1 = (bucketPoint[0][1] - bucketPoint[1][1])/(bucketPoint[0][0] - bucketPoint[1][0])
    # slope1 = math.atan(slope1)
    # slope1 = abs(slope1*180/math.pi)
    
    # slope2 = (bucketPoint[2][1] - bucketPoint[3][1])/(bucketPoint[2][0] - bucketPoint[3][0])
    # slope2 = math.atan(slope2)
    # slope2 = abs(slope2*180/math.pi)

    # print(slope1,slope2)

