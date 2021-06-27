import math
import pyrealsense2 as rs
# 上午的版本，实验中发现有可能两个点的x坐标是一致的，所以必须加上判断分母不为0的条件
# 四个点的情况：打印四个角度，选择最接近90度的。
# 0，0的情况
# TODO: 补全后的四个点仍然可能不对。需要先补全再判断。

# def getPoint(maxBox,centerPoint,aligned_depth_frame,x,y):
#     i = 0
#     point = ([0,0],[0,0],[0,0],[0,0],[0,0])
#     depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
#     for rect_point in maxBox:
#         depth_pixel = [x + rect_point[0][0] - 1,y + rect_point[0][1] - 1]
#         dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
#         camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=depth_pixel, depth=dist_to_center)
#         point[i][0]= camera_coordinate[0]*1000
#         point[i][1]= camera_coordinate[2]*1000
#         i = i + 1
#     depth_pixel = [int(x + centerPoint[0] - 1),int(y + centerPoint[1] - 1)]
#     dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
#     camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=depth_pixel, depth=dist_to_center)
#     point[4][0]= camera_coordinate[0]*1000
#     point[4][1]= camera_coordinate[2]*1000
#     # print("raw data",point)
#     return point


# def completePoint(point):
#     isValid = 0
#     k = ([0]*4)
#     m = ([0]*4)
#     n = -1
#     j = 0

#     # caculate zero point
#     for i in range(3):
#         if point[i][1] == 0:
#             isValid = isValid - 1
#             n = i

#     # if zero point > 1, no use
#     if isValid <= -2:
#         # print("Invalid Data! Too many zeros")
#         return n,([0,0],[0,0],[0,0],[0,0])

#     # if zero point == 1, complete it firstly
#     # if isValid == -1:
#     #     point[n][0] = point[(n+3)%4][0]+point[(n+1)%4][0]-point[(n+2)%4][0]
#     #     point[n][1] = point[(n+3)%4][1]+point[(n+1)%4][1]-point[(n+2)%4][1]
#     if isValid == -1:
#         if point[4][0] == 0:
#             point[n][0] = point[(n+3)%4][0]+point[(n+1)%4][0]-point[(n+2)%4][0]
#             point[n][1] = point[(n+3)%4][1]+point[(n+1)%4][1]-point[(n+2)%4][1]
#         point[n][0] = point[4][0]+point[4][0]-point[(n+2)%4][0]
#         point[n][1] = point[4][1]+point[4][1]-point[(n+2)%4][1]
#         # print("modified data",point)
#         # return n,point

#     #check coordinate
#     for i in range(4):
#         if (point[(i+1)%4][0] - point[i][0]) == 0:
#             return n,([0,0],[0,0],[0,0],[0,0])
#         k[i] =  math.atan((point[(i+1)%4][1] - point[i][1])/(point[(i+1)%4][0] - point[i][0]))

#     # caculate angle deviation
#     for i in range(4):
#         m[i] = abs(abs(k[(i+1)%4]*180/math.pi - k[i]*180/math.pi)-90)
#         # print("angle",m[i])

#     deviation = m[0]
#     for i in range(4):
#         if m[i] < deviation:
#             j = i
#             deviation = m[i]

#     # print(deviation)
#     if deviation < 15:
#         if isValid == -1:
#             print(point)
#             return n,point
#         # print(j)
#         point[(j+2)%4][0] = (point[(j+3)%4][0] + point[(j+1)%4][0]) - point[j][0]
#         point[(j+2)%4][1] = (point[(j+3)%4][1] + point[(j+1)%4][1]) - point[j][1]
#         print(point[0][0])
#         return n,point
#     return n,([0,0],[0,0],[0,0],[0,0])

    # if isValid == -1:
    #     point[n][0] = point[(n+3)%4][0]+point[(n+1)%4][0]-point[(n+2)%4][0]
    #     # print("realsense",point[n][0])
    #     point[n][1] = point[(n+3)%4][1]+point[(n+1)%4][1]-point[(n+2)%4][1]
    #     # point[n][0] = point[n][1]*fux#ux
    #     # print("depth",point[n][0])

    #     print("modified data",point)
    #     return n,point


# 下午版本:运用斜率判断。可能是因为深度有误差，算出来的矩形很难进判断条件，所以把角度阈值给成了60-120，损失应该挺大的，所以就有了下面这一版
# 数据point = ([0,0],[188,776],[131,545],[25,618])算出来矩形角度有110度
# def completePoint(point)
#     isValid = 0

#     k = ([0]*4)
#     for i in range(4):
#         if point[i][1] == 0:
#             isValid = isValid - 1
#     if isValid <= -2:
#         print("Invalid Data! Too many zeros")
#         return
#     if isValid == 0:
#         print("good point",point)
#         return point
    
#     for i in range(4):
#         if (point[(i+1)%4][0] - point[i][0]) == 0:
#             k[i] = 90
#         else:
#             k[i] = math.atan((point[(i+1)%4][1] - point[i][1])/(point[(i+1)%4][0] - point[i][0]))
#             k[i] = k[i]*180/math.pi
#     for i in range(4):
#         m[i] = abs(k[(i+1)%4] - k[i])
#         if m[i]<120 and m[i]> 60:
#             # i+1 的对点有问题，(i) (i+2)%4 正常 (i+3)%4异常
#             point[(i+3)%4][0] = (point[i][0] + point[(i+2)%4][0]) - point[(i+1)%4][0]
#             point[(i+3)%4][1] = (point[i][1] + point[(i+2)%4][1]) - point[(i+1)%4][1]
#             isValid = 1
#             break
#         if isValid == -1:
#             print("not a rectangle")
#             return 
#     print("point",point)
#     return point

# 既然知道有一个点是000所以坐标不对，那就直接用其他三个点求剩下的这个点，不需要判断直角
# def completePoint(point):
#     isValid = 0
#     pointNum = -1
#     k = ([0]*4)
#     for i in range(4):
#         if point[i][1] == 0:
#             isValid = isValid - 1
#             pointNum = i
#     if isValid <= -2:
#         print("Invalid Data! Too many zeros")
#         return
#     if isValid == 0:
#         print("good point",point)
#         return point
    
#     point[pointNum][0] = point[(pointNum+3)%4][0]+point[(pointNum+1)%4][0]-point[(pointNum+2)%4][0]
#     point[pointNum][1] = point[(pointNum+3)%4][1]+point[(pointNum+1)%4][1]-point[(pointNum+2)%4][1]

#     print("point",point)
#     return point

# if __name__ == '__main__':
#     point = ([0,0],[188,776],[131,545],[25,618])
#     point = completePoint(point)


def getPoint(maxBox,centerPoint,aligned_depth_frame,x,y):
    i = 0
    point = ([0,0],[0,0],[0,0],[0,0],[0,0])
    depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics
    for rect_point in maxBox:
        depth_pixel = [x + rect_point[0][0] - 1,y + rect_point[0][1] - 1]
        dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
        camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=depth_pixel, depth=dist_to_center)
        point[i][0]= camera_coordinate[0]*1000
        point[i][1]= camera_coordinate[2]*1000
        i = i + 1
    depth_pixel = [int(x + centerPoint[0] - 1),int(y + centerPoint[1] - 1)]
    dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
    camera_coordinate = rs.rs2_deproject_pixel_to_point(intrin=depth_intrin, pixel=depth_pixel, depth=dist_to_center)
    point[4][0]= camera_coordinate[0]*1000
    point[4][1]= camera_coordinate[2]*1000
    # print("raw data",point)
    return point


def completePoint(point):
    isValid = 0
    k = ([0]*3)
    m = ([0]*4)
    n = -1
    j = 0
    correctPoint = ([0,0],[0,0])

    # caculate zero point
    for i in range(3):
        if point[i][1] == 0:
            isValid = isValid - 1
            n = i

    # if zero point > 1, no use
    if isValid <= -2:
        return ([0,0],[0,0]),0

    # if point[4][0] == 0:
    if isValid == -1:
        return ([0,0],[0,0]),0

    # caculate angle deviation
    for i in range(4):
        # m[i] = abs(point[i][1] - point[(i+1)%4][1])
        m[i] = math.sqrt( (point[i][0] - point[(i+1)%4][0]) * (point[i][0] - point[(i+1)%4][0]) + (point[i][1] - point[(i+1)%4][1]) * (point[i][1] - point[(i+1)%4][1]) )
        # print("angle",m[i])

    deviation = m[0]
    for i in range(4):
        if m[i] < deviation:
            j = i
            deviation = m[i]
            # print(deviation)
    # print(deviation)
    if deviation < 500:
        correctPoint[0][0] = (point[j][0] + point[(j+1)%4][0]) / 2
        correctPoint[0][1] = (point[j][1] + point[(j+1)%4][1]) / 2

        k[0] =  (math.atan((point[j][1] - point[(j+2)%4][1])/(point[j][0] - point[(j+2)%4][0]))) * 180 / math.pi
        k[1] =  (math.atan((point[j][1] - point[(j+3)%4][1])/(point[j][0] - point[(j+3)%4][0]))) * 180 / math.pi
        k[2] =  (math.atan((point[(j+2)%4][1] - point[(j+3)%4][1])/(point[(j+2)%4][0] - point[(j+3)%4][0]))) * 180 / math.pi

        m[0] = abs(k[0]-k[2])
        m[1] = abs(k[1]-k[2])
        # deviation2 = math.sqrt( (point[(j+2)%4][0] - point[(j+3)%4][0]) * (point[(j+2)%4][0] - point[(j+3)%4][0]) + (point[(j+2)%4][1] - point[(j+3)%4][1]) * (point[(j+2)%4][1] - point[(j+3)%4][1]) )
        # deviation2 = abs(point[(j+2)%4][1] - point[(j+3)%4][1]) 
        # print(deviation2)

        # if m[0] < 30 or m[1] < 30:
        #     return n,([0,0],[0,0],[0,0],[0,0])
        if m[0] < 45:
            point[(j+2)%4][0] = point[(j+1)%4][0] + point[(j+3)%4][0] - point[j][0]
            point[(j+2)%4][1] = point[(j+1)%4][1] + point[(j+3)%4][1] - point[j][1]

        if m[1] < 45:
            point[(j+3)%4][0] = point[j][0] + point[(j+2)%4][0] - point[(j+1)%4][0]
            point[(j+3)%4][1] = point[j][1] + point[(j+2)%4][1] - point[(j+1)%4][1]
        # if deviation2 > 500:
        #     return ([0,0],[0,0]),0

        correctPoint[1][0] = (((point[(j+2)%4][0] + point[(j+3)%4][0]) / 2) + correctPoint[0][0]) / 2
        correctPoint[1][1] = (((point[(j+2)%4][1] + point[(j+3)%4][1]) / 2) + correctPoint[0][1]) / 2

        slope = math.atan((correctPoint[1][1]-correctPoint[0][1])/(correctPoint[1][0]-correctPoint[0][0])) * 180 / math.pi
        return correctPoint[1],slope
    return ([0,0],[0,0]),0

    # correctPoint[1][0] = point[4][0]
    # correctPoint[1][1] = point[4][1]

    # for i in range(4):
    #     m[i] = math.sqrt( (point[i][0] - point[(i+1)%4][0]) * (point[i][0] - point[(i+1)%4][0]) + (point[i][1] - point[(i+1)%4][1]) * (point[i][1] - point[(i+1)%4][1]) )
    # # print("angle",m[i])

    # deviation = m[0]
    # for i in range(4):
    #     if m[i] < deviation:
    #         j = i
    #         deviation = m[i]
    #         # print(deviation)

    # if deviation < 5:
    #     correctPoint[0][0] = (point[j][0] + point[(j+1)%4][0]) / 2
    #     correctPoint[0][1] = (point[j][1] + point[(j+1)%4][1]) / 2

    #     slope = math.atan((correctPoint[1][1]-correctPoint[0][1])/(correctPoint[1][0]-correctPoint[0][0])) * 180 / math.pi

    #     return correctPoint[1],slope
    # return ([0,0],[0,0]),0
