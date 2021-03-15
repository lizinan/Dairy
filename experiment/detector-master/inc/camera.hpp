#ifndef __CAMERA_H
#define __CAMERA_H
#include "include-opencv.hpp"
#include "include-realsense.hpp"
#include "projection.hpp"

namespace cam
{
class Camera
{
private:
public:
    Camera() : frame_size(640, 480), status(STOP) {};
    Camera(int w, int h) : frame_size(w, h), status(STOP) {};
    virtual ~Camera() {};
    virtual bool open() = 0;
    virtual bool isOpen() = 0;
    virtual void close() = 0;

    cv::Size frame_size;
    int real_fps;
    cv::Mat extrin_rmat;
    cv::Mat extrin_tmat;
    cv::Mat intrin_mat;
    cv::Mat distortion;
    enum Status {
        WORK,
        PAUSE,
        STOP
    } status;
};

class USBCam : public Camera
{
private:
    int camera;
    cv::VideoCapture capture;
public:
    USBCam(int cid) : camera(cid) {}
    USBCam(int w, int h, int cid) : Camera(w, h), camera(cid) {}
    ~USBCam() { close(); }
    bool open();
    bool isOpen();
    void close();
    cv::Mat read();
};

class RsCam : public Camera
{
private:
    /* data */
    rs2_intrinsics color_intrinics;
    rs2_intrinsics depth_intrinics;
    rs2::config cfg;
    rs2::pipeline pipe;
    rs2::align align_to_depth;
    rs2::align align_to_color;
    int setting_fps;
    proj::Projection projector;
public:
    RsCam() 
    : setting_fps(60),
    align_to_depth(RS2_STREAM_DEPTH),
    align_to_color(RS2_STREAM_COLOR) {}
    RsCam(int w, int h, int s_fps);
    ~RsCam() { close(); }
    bool open();
    bool isOpen();
    void close();
    cv::Mat read();
    void readTo(cv::Mat &color, cv::Mat &depth);
    rs2_intrinsics getIntrinstics(){return projector.getIntrinsics();};

    struct Config {
        bool align_to_depth;
        Config() : align_to_depth(true) {}
    } config;
};
} // namespace cam

#endif