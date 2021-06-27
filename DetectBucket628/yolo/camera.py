import cv2
import detect
import numpy as np

cap=cv2.VideoCapture(4)
a = detect.detectapi(weights='weights/426.pt')
while True:
    #img = cv2.imread('data/images/75.jpg')
    rec,img = cap.read()

    result,names =a.detect([img])
    img=result[0][0] #第一张图片的处理结果图片

    #print(result)

    cv2.imshow("vedio",img)

    if cv2.waitKey(1)==ord('q'):
        break

# '''
# for cls,(x1,y1,x2,y2),conf in result[0][1]: #第一张图片的处理结果标签。q
#     print(cls,x1,y1,x2,y2,conf)
#     cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0))
#     cv2.putText(img,names[cls],(x1,y1-20),cv2.FONT_HERSHEY_DUPLEX,1.5,(255,0,0))
# '''
m = result[0][1][0][1]
#print(m)
#n = m[0][1][0]
#print(n)
#t = n[1][1]
#print(t)

roi = (m[0],m[1],m[2]-m[0]+1,m[3]-m[1]+1)
x, y, w, h = roi
#print(roi)
# 显示ROI并保存图片
if roi != (0, 0, 0, 0):
    crop = img[y:y+h, x:x+w]
    cv2.imshow('crop', crop)
    cv2.imwrite('crop.jpg', crop)
    print('Saved!')

src = cv2.imread('crop.jpg')
hsvFrame = cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
cv2.imshow('hsvFrame',hsvFrame)

lowerHSV = np.array([0,0,0])
upperHSV = np.array([180,120,110])
mask = cv2.inRange(hsvFrame,lowerHSV,upperHSV)
cv2.imshow('ir',mask)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
binary = cv2.morphologyEx(mask, cv2.MORPH_OPEN,kernel)
#binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN,kernel)
#blurFrame = cv2.medianBlur(binary,1)
cv2.imshow('hhh',binary)
#cv2.imshow('h',blurFrame)

#img = cv2.GaussianBlur(binary,(3,3),0)
#cv2.imshow('gaussian',img)
canny = cv2.Canny(binary, 50, 150)
cv2.imshow('canny',canny)

contours, hierarchy = cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)  

cv2.drawContours(src,contours,-1,(0,0,255),3)  

cv2.imshow("img", src)  

maxArea = 0
maxBox = 0
for cont in contours:
    # 对每个轮廓点求最小外接矩形
    rect = cv2.minAreaRect(cont)
    # cv2.boxPoints可以将轮廓点转换为四个角点坐标
    box = cv2.boxPoints(rect)
    # 这一步不影响后面的画图，但是可以保证四个角点坐标为顺时针
    startidx = box.sum(axis=1).argmin()
    box = np.roll(box,4-startidx,0)
    # 在原图上画出预测的外接矩形
    box = box.reshape((-1,1,2)).astype(np.int32)
    area = cv2.contourArea(box)
    if area > maxArea:
        maxArea = area
        maxBox = box
    print(area)
print("show box")
print(maxBox)
print(maxBox[0])
print(maxBox[0][0])
print(maxBox[1][0])
print(maxBox[1][0][0])

for rect_point in box:
    depth_pixel = [x + rect_point[0][0],y+rect_point[0][1]]
    print(depth_pixel)
img = cv2.polylines(src,[maxBox],True,(0,255,0),1)
cv2.imshow('test',img)
cv2.waitKey(0)

