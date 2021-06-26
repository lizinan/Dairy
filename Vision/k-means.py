import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import cv2
import pyrealsense2 as rs
import detect


def show(winname,src):
    cv2.namedWindow(winname,cv2.WINDOW_GUI_NORMAL)
    cv2.imshow(winname,src)
    cv2.waitKey()

def getJointContours():
    pass

def processData():
    pass

a = detect.detectapi(weights='weights/609.pt')

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)

while 1:
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())

    results,names =a.detect([color_image])
    if results[0][1] == []:
        continue
    result = results[0][1][0]
    m = result[1]
    roi = (m[0] ,m[1] ,m[2]-m[0]  ,m[3]-m[1])
    x, y, w, h = roi
    if x - 25 <= 0:
        x = 0
    else:
        x = x - 25
    if y - 25 <= 0:
        y = 0
    else:
        y = y - 25
    if w + x + 25 >= 639 :
        w = 639 - x
    else:
        w = w + 50
    if h + y + 25 >= 479:
        h = 479 - y
    else:
        h = h + 50

    src = color_image[y:y+h, x:x + w ]
    #### 得到头部和尾部的轮廓 ####
    headContours,tailContours = getJointContours(src)
    #### 串联所有的大轮廓 ####
    #### k-means取得中心 ####
    headData,tailData = processData(headContours,tailContours)
    X = np.array([[1, 2], [1, 4], [1, 0],
               [10, 2], [10, 4], [10, 0]])

    centers = []
    cost = []
    for i in range(2):
        k = i + 1
        kmeans = KMeans(n_clusters=k, random_state=0).fit(X)
        centers.append(kmeans.cluster_centers_)
        cost.append(kmeans.score(X))
    if cost[0] < cost[1]:# 1
        #### 处理一只箭 ####
        pass
    else:
        #### 2 ####
        centers = centers[1]






    img = color_image[y:y+h,x:x+w]
    o = img.copy()
    print(img.shape)
    # 将一个像素点的rgb值作为一个单元处理，这一点很重要
    data = img.reshape((-1,3))
    print(data.shape)
    # 转换数据类型
    data = np.float32(data)
    # 设置Kmeans参数
    critera = (cv2.TermCriteria_EPS+cv2.TermCriteria_MAX_ITER,10,0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    # 对图片进行四分类
    r,best,center = cv2.kmeans(data,4,None,criteria=critera,attempts=10,flags=flags)
    print(r)
    print(best.shape)
    print(center)
    center = np.uint8(center)
    # 将不同分类的数据重新赋予另外一种颜色，实现分割图片
    data[best.ravel()==1] = (0,0,0)
    data[best.ravel()==0] = (255,0,0) 
    data[best.ravel()==2] = (0,0,255)
    data[best.ravel()==3] = (0,255,0) 
    # 将结果转换为图片需要的格式
    data = np.uint8(data)
    oi = data.reshape((img.shape))
    # 显示图片
    show('img',img)
    show('res',oi)
