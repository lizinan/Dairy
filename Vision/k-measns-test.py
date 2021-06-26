from typing import Counter
from numpy import unique
from numpy import where
from sklearn.datasets import make_classification
from sklearn.cluster import KMeans,DBSCAN,mean_shift
from sklearn.mixture import GaussianMixture
from matplotlib import pyplot
import matplotlib
import cv2
import pyrealsense2 as rs
import detect
import numpy as np

def getAllContours(crop):
    hsvFrame = cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)

    ##### 设置箭头阈值 #####
    headLowerHsv = np.array([30,30,120])
    headUpperHsv = np.array([120,255,255])
    headMask = cv2.inRange(hsvFrame,headLowerHsv,headUpperHsv)
    # cv2.imshow('headMask',headMask)
    ##### 设置箭尾阈值 #####
    tailLowerHsv = np.array([0,120,60])
    tailUpperHsv = np.array([60,255,255])
    tailMask = cv2.inRange(hsvFrame,tailLowerHsv,tailUpperHsv)
    # cv2.imshow('tailMask',tailMask)

    headBlur= cv2.medianBlur(headMask,3)#模糊处理，降低计算量
    headKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    headClose = cv2.morphologyEx(headBlur, cv2.MORPH_CLOSE,headKernel)#闭操作，填充轮廓
    #cv2.imshow('headBlur',headBlur)
    cv2.imshow('headopen',headClose)
    #得到箭头轮廓
    headContours, headHierarchy = cv2.findContours(headClose,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(crop,headContours,-1,(0,0,255),3)    

    tailBlur = cv2.medianBlur(tailMask,3)
    tailKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    tailOpen = cv2.morphologyEx(tailBlur, cv2.MORPH_OPEN,tailKernel)
    # cv2.imshow('tailBlur',tailBlur)
    cv2.imshow('tailOpen',tailOpen)
    cv2.imshow('crop',crop)
    # 得到箭尾轮廓
    tailContours, tailHierarchy= cv2.findContours(tailOpen,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    return headContours,tailContours  

def transContours(Contours):
    strCatContours = []
    for i in range(len(Contours)):
        for j in range(len(Contours[i])):
            strCatContours = strCatContours + Contours[i][j].tolist()
    return strCatContours

def ChooseContours(headContours,tailContours):
    headMinArea = 800
    strCatHeadCont = []
    for i in range(len(headContours)):
        rect = cv2.minAreaRect(headContours[i])
        headArea = cv2.contourArea(headContours[i])
        if headArea > headMinArea:
            for j in range(len(headContours[i])):
                strCatHeadCont = strCatHeadCont + headContours[i][j].tolist()

    strCatTailCont = []
    tailMinArea = 300
    for i in range(len(tailContours)):
        tailArea = cv2.contourArea(tailContours[i])
        if tailArea > tailMinArea:
            for j in range(len(tailContours[i])):
                strCatTailCont = strCatTailCont + tailContours[i][j].tolist()
    return strCatHeadCont,strCatTailCont

matplotlib.use('TkAgg')
color_image = cv2.imread("120.jpg")
crop = color_image

headContours,tailContours = getAllContours(crop)
# headDat = transContours(headContours)
# tailDat = transContours(tailContours)
headDat,tailDat = ChooseContours(headContours,tailContours)

# 定义数据集
headDat = np.array(headDat)
tailDat = np.array(tailDat)
X = tailDat

## DBSCAN
# model = DBSCAN(eps=0.30, min_samples=9)
# yhat = model.fit_predict(X)

#KMEANS
# model = KMeans(n_clusters=5)
# model.fit(X)
# yhat = model.predict(X)

##MEANSHIFT   
# model = MeanShift()
# yhat = model.fit_predict(X)

##Gaussian
model = GaussianMixture(n_components=3)
model.fit(X)
yhat = model.predict(X)

# 检索唯一群集
clusters = unique(yhat)
# 为每个群集的样本创建散点图
for cluster in clusters:
# 获取此群集的示例的行索引
    row_ix = where(yhat == cluster)
    # 创建这些样本的散布
    pyplot.scatter(X[row_ix, 0], X[row_ix, 1])
    # 绘制散点图
pyplot.show()






























# a = detect.detectapi(weights='weights/609.pt')

# pipeline = rs.pipeline()
# config = rs.config()
# config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
# pipe_profile = pipeline.start(config)

# matplotlib.use('TkAgg')

# while 1:
#     frames = pipeline.wait_for_frames()
#     color_frame = frames.get_color_frame()
#     color_image = np.asanyarray(color_frame.get_data())

#     results,names =a.detect([color_image])
#     if results[0][1] == []:
#         continue
#     result = results[0][1][0]
#     m = result[1]
#     roi = (m[0] ,m[1] ,m[2]-m[0]  ,m[3]-m[1])
#     x, y, w, h = roi
#     if x - 25 <= 0:
#         x = 0
#     else:
#         x = x - 25
#     if y - 25 <= 0:
#         y = 0
#     else:
#         y = y - 25
#     if w + x + 25 >= 639 :
#         w = 639 - x
#     else:
#         w = w + 50
#     if h + y + 25 >= 479:
#         h = 479 - y
#     else:
#         h = h + 50

#     crop = color_image[y:y+h, x:x+w]

#     headContours,tailContours = getAllContours(crop)
#     headContours,tailContours = transContours(headContours,tailContours)
#     headDat = headContours[0]
#     tailDat = tailContours[0]

#     # 定义数据集
#     #X, _ = make_classification(n_samples=1000, n_features=2, n_informative=2, n_redundant=0, n_clusters_per_class=1, random_state=4)
#     headDat = np.array(headDat)
#     tailDat = np.array(tailDat)
#     X = headDat


#     # 定义模型
#     model = DBSCAN(eps=0.30, min_samples=9)
#     # 模型拟合与聚类预测
#     yhat = model.fit_predict(X)


#     # 定义模型
#     #model = KMeans(n_clusters=2)
#     # 模型拟合
#     # model.fit(X)
#     # 为每个示例分配一个集群
#     # yhat = model.predict(X)
#     # 检索唯一群集
#     clusters = unique(yhat)
#     # 为每个群集的样本创建散点图
#     for cluster in clusters:
#     # 获取此群集的示例的行索引
#         row_ix = where(yhat == cluster)
#         # 创建这些样本的散布
#         pyplot.scatter(X[row_ix, 0], X[row_ix, 1])
#         # 绘制散点图
#     pyplot.show()

