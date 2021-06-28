import numpy as np
import imageio
from sklearn.cluster import KMeans

def image_cluster(image_name, save_name, k_cluster=3):
    """
    cluster by KMeans for RGB image
    """
    
    # 1:read image
    image = imageio.imread(image_name)

    # 2: convert (w, h, 3) into (w*h, 3)
    # R,G and B combine as 3 features 
    # data will be a 2D matrix, each row have 3 values(R/G/B),
    # and each column has width*height values
    # this operation convert 3D to 2D, like reshape 
    image2matrix = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            r_v, g_v, b_v = image[i, j]
            image2matrix.append([r_v/255.0, g_v/255.0, b_v/255.0])
    data = np.mat(image2matrix)

    # 3: cluster, I thought: give every pixel (that in orignal image)
    #    a label , so the label have same shape as image(gray)
    cls = KMeans(n_clusters=k_cluster).fit_predict(data)
    cls = cls.reshape(image.shape[0], image.shape[1])
    
    # 4: create a image container
    container = np.zeros(shape=(image.shape[0], image.shape[1]))

    # 5: use cluster labels as "gray value" 
    #    and  fill it into aimage container
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            # cls[i, j]*30 ,because label value is 0, 1, 2
            # the bright difference betwwen labels is to small
            container[i, j] = cls[i, j]*60

    # 6: saver the cluster image
    container = container.astype(np.uint8) 
    imageio.imsave(save_name, container)
    
    return True

image_cluster("90.jpg", "cluster.jpg")