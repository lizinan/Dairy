#include "projection.hpp"
#include <iostream>

namespace proj
{
cv::Point3f Projection::pixel2world(const cv::Point2i &pixel,const cv::Mat &depth) const {
    cv::Point3f cam_point = pixel2camera(pixel, depth);
    return camera2world(cam_point);
}

cv::Point3f Projection::pixel2camera(const cv::Point2i &pixel,const cv::Mat &depth) const {
    float pixel_point[2] = {(float)pixel.x, (float)pixel.y};
    float point[3] = {0};
    double dist = depth.at<uint16_t>(pixel.y, pixel.x);
    rs2_deproject_pixel_to_point(point, &_intrinsics, pixel_point, dist);
    //std::cout<<_intrinsics.fx<<'\t'<<_intrinsics.fy<< '\t'<<_intrinsics.height<<std::endl;
    return cv::Point3f(point[0], point[1], point[2]);
}   

cv::Point3f Projection::camera2world(const cv::Point3f point) const {
    cv::Mat p_c = cv::Mat(cv::Matx31f(point.x, point.y , point.z));
    cv::Mat p_w;
    cv::Mat rmat = _extrin_rmat.t();
    p_w = rmat * (p_c - _extrin_tmat);

    return cv::Point3f(p_w.at<float>(0), p_w.at<float>(1), p_w.at<float>(2));
}


} // namespace proj
