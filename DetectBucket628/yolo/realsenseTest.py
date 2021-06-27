import pyrealsense2 as rs
import numpy as np
import cv2

# TODO：训练yolo神经网络
# TODO:从yolo程序中获取坐标。先以realsense测试
# TODO:循环调用
# TODO:将yolo返回的坐标进行处理，因为yolo返回的是裁剪后的图片坐标

# TODO:测试深度图的准确性
pipeline = rs.pipeline()
pc = rs.pointcloud()

config = rs.config()

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)

pipe_profile = pipeline.start(config)

while 1:
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    align_to = rs.stream.color
    align = rs.align(align_to)
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()

    # Intrinsics & Extrinsics
    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
    color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
    color_to_depth_extrin = color_frame.profile.get_extrinsics_to(depth_frame.profile)
    depth_to_color_extrin = depth_frame.profile.get_extrinsics_to(color_frame.profile)

    depth_sensor = pipe_profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    # Depth scale - units of the values inside a depth frame, i.e how to convert the value to units of 1 meter
    depth_pixel = [575,354]
    dist_to_center = aligned_depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
    print("depth")
    print(dist_to_center)
    test = depth_frame.get_distance(depth_pixel[0],depth_pixel[1])
    print("test")
    print(test)
    # depth_data = np.asanyarray(depth_frame.get_data(), dtype="float16")
    # print("depth_data")
    # print(depth_data)
    # depth = depth_data[1]
    # distance = depth*0.001
    # print("distance")
    # print(distance)


# TODO: 写串口
pipeline.stop()






# pipeline = rs.pipeline()
# config = rs.config()
# profile = pipeline.start(config)
# frames = pipeline.wait_for_frames()
# depth_frame = frames.get_depth_frame()
# color_frame = frames.get_color_frame()
# depth_scale = 0.001 #depth to distance
# depth_min = 0.12 #meter
# depth_max = 3.0 #meter

# depth_intrin = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
# color_intrin = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()

# depth_to_color_extrin =  profile.get_stream(rs.stream.depth).as_video_stream_profile().get_extrinsics_to( profile.get_stream(rs.stream.color))
# color_to_depth_extrin =  profile.get_stream(rs.stream.color).as_video_stream_profile().get_extrinsics_to( profile.get_stream(rs.stream.depth))

# color_point = [340,94]

# depth_point_ = rs.rs2_project_color_pixel_to_depth_pixel(
#             depth_frame.get_data(), depth_scale,
#             depth_min, depth_max,
#             depth_intrin, color_intrin, depth_to_color_extrin, color_to_depth_extrin, color_point)

# print(depth_point_)            