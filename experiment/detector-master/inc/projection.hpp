#ifndef __PROJECTION_H
#define __PROJECTION_H
#include "include-opencv.hpp"
#include "include-realsense.hpp"

namespace proj
{
class Projection
{
private:
    /* data */
    cv::Mat _extrin_rmat;
    cv::Mat _extrin_tmat;
    rs2_intrinsics _intrinsics;
public:
    Projection()
        :_extrin_rmat(cv::Mat(cv::Matx33f(0.99931884f, -0.012486592f, 0.034726303f,
                                          0.01203839f, 0.99984193f, 0.013085966f,
                                          -0.034884211f, -0.012659003f, 0.99931121f))),
        _extrin_tmat(cv::Mat(cv::Matx31f(148.75751f,
                                         -399.74771f,
                                         -383.60397f)))
        {}
    Projection(const cv::Mat rmat,const cv::Mat tmat,const rs2_intrinsics intrin) 
        : _extrin_rmat(rmat),
        _extrin_tmat(tmat),
        _intrinsics(intrin) {};
    ~Projection() {};
    void setIntrin(const rs2_intrinsics &intrin) { _intrinsics = intrin;}
    cv::Point3f pixel2world(const cv::Point2i &pixel,const cv::Mat &depth) const;
    cv::Point3f pixel2camera(const cv::Point2i &pixel,const cv::Mat &depth) const;
    cv::Point3f camera2world(const cv::Point3f point) const;
    rs2_intrinsics getIntrinsics(){return _intrinsics;};
};

} // namespace proj


#endif