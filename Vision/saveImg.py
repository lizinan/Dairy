import cv2
import pyrealsense2 as rs
import numpy as np


pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)
pipe_profile = pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)

i = 0
while True:

        # get color_img, depth_img
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    aligned_frames = align.process(frames)
    color_image = np.asanyarray(color_frame.get_data())
    cv2.imshow('RealSense', color_image)

    if cv2.waitKey(1)==ord('q'):
        break
    elif cv2.waitKey(1)==ord('s'): # wait for 's' key to save and exit
        cv2.imwrite(('%d.jpg'%i),color_image)
        i = i + 1
        print("saved!",i)
        cv2.destroyAllWindows()