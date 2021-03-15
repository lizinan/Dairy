#include "results.hpp"

namespace results {
void Result::drawBoundingBox(cv::Mat &src) {
    cv::Point2f points[4];
    boundingBox.points(points);
    for (int i = 0; i < 4; i++) {
        cv::line(src, points[i], points[(i + 1) % 4], cv::Scalar::all(0), 2);
    }
}
cv::Point2f Result::centroid() {
    return boundingBox.center;
}
}