#include "camera.hpp"
#include <iostream>

namespace cam
{
bool USBCam::open() try {
    capture = cv::VideoCapture(camera);
    status = WORK;
    return true;
} catch (cv::Exception &e) {
    std::cout << "while opening usb camera : " << e.what() << std::endl;
    status = STOP;
    return false;
}

bool USBCam::isOpen() {
    return capture.isOpened();
}

void USBCam::close() {
    if (status != STOP) capture.release();
    status = STOP;
}

cv::Mat USBCam::read() {
    cv::Mat frame;
    capture >> frame;
    return frame;
}

RsCam::RsCam(int w, int h, int s_fps)
        : Camera(w, h),
        align_to_depth(RS2_STREAM_DEPTH),
        align_to_color(RS2_STREAM_COLOR),
        setting_fps(s_fps) {
    
}

bool RsCam::open() try {
    cfg.enable_stream(RS2_STREAM_COLOR, frame_size.width, frame_size.height, RS2_FORMAT_BGR8, setting_fps);
    cfg.enable_stream(RS2_STREAM_DEPTH, frame_size.width, frame_size.height, RS2_FORMAT_Z16, setting_fps);
    cfg.enable_stream(RS2_STREAM_INFRARED, 1, frame_size.width, frame_size.height, RS2_FORMAT_Y8, setting_fps);
    cfg.enable_stream(RS2_STREAM_INFRARED, 2, frame_size.width, frame_size.height, RS2_FORMAT_Y8, setting_fps);
    rs2::pipeline_profile profile = pipe.start(cfg);
    color_intrinics = profile.get_stream(RS2_STREAM_COLOR).as<rs2::video_stream_profile>().get_intrinsics();
    depth_intrinics = profile.get_stream(RS2_STREAM_DEPTH).as<rs2::video_stream_profile>().get_intrinsics();
    if (config.align_to_depth)
        projector.setIntrin(depth_intrinics);  
    else
        projector.setIntrin(color_intrinics);
    status = WORK;
    return true;
} catch (rs2::error &e) {
    std::cout << "while opening realsense camera : " << e.what() << std::endl;
    status = STOP;
    return false;
}

bool RsCam::isOpen() {
    return status != STOP;
}

void RsCam::close() {
    if (status != STOP) pipe.stop();
    status = STOP;
}

cv::Mat RsCam::read() {
    rs2::frameset fset = pipe.wait_for_frames();
    if (config.align_to_depth)
        fset = align_to_depth.process(fset);
    else
        fset = align_to_color.process(fset);
    rs2::frame color_frame = fset.get_color_frame();
    return cv::Mat(frame_size, CV_8UC3, (void*)color_frame.get_data(), cv::Mat::AUTO_STEP);
}

void RsCam::readTo(cv::Mat &color, cv::Mat &depth) {
    rs2::frameset fset = pipe.wait_for_frames();
    if (config.align_to_depth)
        fset = align_to_depth.process(fset);
    else
        fset = align_to_color.process(fset);
    rs2::frame color_frame = fset.get_color_frame();
    color = cv::Mat(frame_size, CV_8UC3, (void*)color_frame.get_data(), cv::Mat::AUTO_STEP);
    rs2::frame depth_frame = fset.get_depth_frame();
    depth = cv::Mat(frame_size, CV_16UC1, (void*)depth_frame.get_data(), cv::Mat::AUTO_STEP);
}
} // namespace cam
