import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
 
class DominantColors:
 
    CLUSTERS = None
    IMAGE = None
    FLAT_IMAGE = None
    COLORS = None
    LABELS = None
    
    def __init__(self, image, clusters=3):
        self.CLUSTERS = clusters
        self.IMAGE = image
    
    def dominantColors(self):
 
        img = self.IMAGE
        gray=cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  #转灰度图
        L,store=[],[]
        for i in range(gray.shape[0]):
            for j in range(gray.shape[1]): 
                if gray[i][j]<156:  
                    L.append((i,j))
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if (i,j) in L:
                    store.append(img[i][j])   #根据最佳前后景分离值将前景的像素值保存下来
        img=np.array(store)
        #reshaping to a list of pixels
        #img = img.reshape((img.shape[0] * img.shape[1], 3))
        
        #save image after operations
        self.FLAT_IMAGE = img
        
        #using k-means to cluster pixels
        kmeans = KMeans(n_clusters = self.CLUSTERS)
        kmeans.fit(img)
        
        #getting the colors as per dominance order
        self.COLORS = kmeans.cluster_centers_
        
        #save labels
        self.LABELS = kmeans.labels_
        
        return self.COLORS.astype(int)
                
    def plotHistogram(self):
       
        #labels form 0 to no. of clusters
        numLabels = np.arange(0, self.CLUSTERS+1)
       
        #create frequency count tables    
        (hist, _) = np.histogram(self.LABELS, bins = numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        
        #appending frequencies to cluster centers
        colors = self.COLORS
        
        #descending order sorting as per frequency count
        colors = colors[(-hist).argsort()]
        hist = hist[(-hist).argsort()] 
        
        #creating empty chart
        chart = np.zeros((50, 500, 3), np.uint8)
        start = 0
        
        #creating color rectangles
        for i in range(self.CLUSTERS):
            end = start + hist[i] * 500
            
            #getting rgb values
            r = colors[i][0]
            g = colors[i][1]
            b = colors[i][2]
            
            #using cv2.rectangle to plot colors
            cv2.rectangle(chart, (int(start), 0), (int(end), 50), (r,g,b), -1)
            start = end	
        
        #display chart
        plt.figure()
        plt.axis("off")
        plt.imshow(chart)
        plt.show()
        
    def rgb_to_hex(self, rgb):
        return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    
    def plotClusters(self):
        #plotting 
        fig = plt.figure()
        ax = Axes3D(fig)        
        for label, pix in zip(self.LABELS, self.FLAT_IMAGE):
            ax.scatter(pix[0], pix[1], pix[2], color = self.rgb_to_hex(self.COLORS[label]))
        plt.show()
        
    def colorPixels(self):
        
        shape = self.IMAGE.shape
        
        img = np.zeros((shape[0] * shape[1], 3))
        labels = self.LABELS
 
        for i,color in enumerate(self.COLORS):
            
            indices = np.where(labels==i)[0]
            
            for index in indices:
                img[index] = color
        
        img = img.reshape((shape[0], shape[1], 3)).astype(int)
        
        #display img
        plt.figure()
        plt.axis("off")
        plt.imshow(img)
        plt.show()