import numpy as np

#r_mat t_mat均只考虑了二维坐标旋转。如果需要加上三维的可以直接改传入的参数和两个矩阵。
def transform2world(point):
    t_matrix = np.mat([30.40057,11.500969])
#     rmat[0.99998873, 0.00073200034, 0.0046958695;
#  -0.00088530808, 0.99946386, 0.032728806;
#  -0.0046693943, -0.032732595, 0.99945325]
    r_matrix = np.mat([[0.99998873,0.0046958695],[-0.0046693943,0.99945325]])

    temp = np.dot((point - t_matrix),r_matrix)
    temp = np.array(temp)
    temp = temp[0]
    temp = np.array(temp)
    world_coordinate[2*i] = int(temp[0])
    world_coordinate[2*i+1] = int(temp[1])
#     tmat[30.40057;
#  -163.62056;
#  11.500969]


    # temp = []
    # world_coordinate = ([0]*8)
    
    # for i in range(4):
    #     temp = np.dot((point[i] - t_matrix),r_matrix)
    #     temp = np.array(temp)
    #     temp = temp[0]
    #     temp = np.array(temp)
    #     world_coordinate[2*i] = int(temp[0])
    #     world_coordinate[2*i+1] = int(temp[1])

    # print("world coordinate",world_coordinate) #打印出来的变量前面总有一个mat，不知道为什么，但是在for里面打印world_coordinate[i]就没问题
    return world_coordinates

# test file
# point = [(1,2),(3,4),(5,6),(7,9)]
# t_matrix = np.mat([0,0])
# r_matrix = np.mat([[1,0],[1,0]])

# world_coordinate = ([0]*4)
# print(world_coordinate)
# for i in range(4):
#     world_coordinate[i] = np.dot((point[i] - t_matrix),r_matrix)
#     print("dot_B",r_matrix)
#     print("dot A",(point[i] - t_matrix))
#     print("dot_result",world_coordinate[i])

# print(world_coordinate)