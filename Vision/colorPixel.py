
from dominantColors import DominantColors
import cv2
#open image
img = '90.jpg'
img = cv2.imread(img)
#在OpenCV中，图像是用BGR来存贮的
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#no. of clusters
clusters = 5
#initialize using constructor
dc = DominantColors(img, clusters)
#print dominant colors
colors = dc.dominantColors()
print(colors)
#display clustered points
dc.colorPixels()
