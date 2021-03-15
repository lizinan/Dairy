#include "detector.hpp"

namespace dt {
void BucketDetector::detect(const cv::Mat &src)
{
    input_info.src = src;
    processImg();
    findComponents();
    analyseComponents();
    visualize();
    return;
}

void BucketDetector::processImg() {
    cv::Mat tmp;
    ++input_info.frame_num;
    cv::GaussianBlur(input_info.src, tmp, cv::Size(3, 3), 0);
    extract_color(tmp, process_info.redBin, RED);
    extract_color(tmp, process_info.blueBin, BLUE);
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
    cv::morphologyEx(process_info.redBin, process_info.redBin, cv::MORPH_OPEN, kernel);
    cv::morphologyEx(process_info.blueBin, process_info.blueBin, cv::MORPH_OPEN, kernel);
}

void BucketDetector::findComponents() {
    findByColorMask(process_info.redBin, RED);
    findByColorMask(process_info.blueBin, BLUE);
}

void BucketDetector::findByColorMask(const cv::Mat &mask, const COLOR &color) {
    using Hierachy = std::vector<cv::Vec4i>;

    Contours contours;
    Hierachy hierachy;
    cv::findContours(mask, contours, hierachy, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    if (color == RED) {
        process_info.red_contours.swap(contours);
    } else if (color == BLUE) {
        process_info.blue_contours.swap(contours);
    }
}

void Detector::extract_color(const cv::Mat &src, cv::Mat &dst, const Detector::COLOR color) const
{
    cv::Mat hsv;
    cv::cvtColor(src, hsv, cv::COLOR_BGR2HSV);
    cv::Scalar hsv_red1_low(0, 150, 46);
    cv::Scalar hsv_red1_high(6, 255, 255);
    cv::Scalar hsv_red2_low(156, 150, 46);
    cv::Scalar hsv_red2_high(180, 255, 255);
    cv::Scalar hsv_blue_low(100, 100, 46);
    cv::Scalar hsv_blue_high(124, 255, 255);
    if (color == RED) {
        cv::Mat red_frame_1, red_frame_2;
        cv::inRange(hsv, hsv_red1_low,
                               hsv_red1_high,
                               red_frame_1);
        cv::inRange(hsv, hsv_red2_low,
                               hsv_red2_high,
                               red_frame_2);
        cv::bitwise_or(red_frame_1, red_frame_2, dst);
        return;
    } else if (color == BLUE) {
        cv::inRange(hsv, hsv_blue_low,
                               hsv_blue_high,
                               dst);
        return;
    }
}

void BucketDetector::analyseComponents() {
    output_info.results.clear();    // not using pre knowledge
    analyseComponentsByColor(RED);
    analyseComponentsByColor(BLUE);
}

void BucketDetector::analyseComponentsByColor(const COLOR &color) {
    Contours dest;
    if (color == RED) {
        dest = process_info.red_contours;
    } else if (color == BLUE) {
        dest = process_info.blue_contours;
    }
    for (auto& contour : dest) {
        results::BucketResult result;
        constexpr int area_min = 500;
        constexpr double eps = 60;
        cv::RotatedRect rect = cv::minAreaRect(contour);
        double area = cv::contourArea(contour);
        if (!(area > area_min && std::fabs(static_cast<double>(rect.angle)) < eps 
            && area >= 0.8 * static_cast<double>(rect.size.area()))) continue;
        if (color == RED) result.color = results::BucketResult::RED;
        else result.color = results::BucketResult::BLUE;
        result.boundingBox = rect;
        output_info.results.emplace_back(result);
    }
}

void BucketDetector::visualize() {
    if (!visual_config.visible) return;
    output_info.visualized_img = input_info.src;
    if (visual_config.showRedBin) { output_info.visualized_img = process_info.redBin; }
    else if (visual_config.showBlueBin) { output_info.visualized_img = process_info.blueBin; }
    else if (visual_config.showRedAndBlueBin) { cv::bitwise_or(process_info.blueBin, process_info.redBin, output_info.visualized_img); }
    else {
        for (auto& res : output_info.results) {
            res.drawBoundingBox(output_info.visualized_img);
        }
        std::stringstream ss;
        ss << "total frames : " << input_info.frame_num;
        cv::putText(output_info.visualized_img, ss.str(), cv::Point(10, 20), cv::FONT_HERSHEY_PLAIN, 1, cv::Scalar::all(0), 1);
    }
}
}
