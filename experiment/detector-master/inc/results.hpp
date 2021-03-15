#ifndef __RESULTS_H
#define __RESULTS_H
#include "include-opencv.hpp"
namespace results {
struct Result {
    cv::RotatedRect boundingBox;
    int id;

    void drawBoundingBox(cv::Mat &src);
    cv::Point2f centroid();
};
struct BucketResult : public Result {
    enum color {
        RED = 0,
        BLUE
    } color;
};
}
#endif