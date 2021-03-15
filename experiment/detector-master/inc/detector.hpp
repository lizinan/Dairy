#ifndef COLORDETECT_H
#define COLORDETECT_H
#include "include-opencv.hpp"
#include "results.hpp"

namespace dt {
class Detector
{
public:
    using Contour = std::vector<cv::Point>;
    using Contours = std::vector<Contour>;
    enum COLOR {
        RED = 0,
        BLUE,
        BLACK
    };
    Detector() {}
    virtual ~Detector() {};
    void extract_color(const cv::Mat &src, cv::Mat &dst, const COLOR color) const;
private:
};

class BucketDetector : public Detector {
public:
    void detect(const cv::Mat &src);
    BucketDetector() {};
    ~BucketDetector() {};
    struct OutputInfo {
        std::vector<results::BucketResult> results;
        cv::Mat visualized_img;
    } output_info;
    struct VisualConfig {
        bool visible;
        bool showRes;
        bool showRedBin;
        bool showBlueBin;
        bool showRedAndBlueBin;
        VisualConfig() 
            : visible(false)
            , showRes(false)
            , showRedBin(false)
            , showBlueBin(false)
            , showRedAndBlueBin(false) {}
    } visual_config;
private:
    void processImg();
    void findComponents();
    void findByColorMask(const cv::Mat &mask, const COLOR &color);
    void analyseComponents();
    void analyseComponentsByColor(const COLOR &color);
    void visualize();

    struct InputInfo {
        cv::Mat src;
        std::size_t frame_num = 0;
    } input_info;
    struct ProcessInfo {
        cv::Mat blueBin;
        cv::Mat redBin;
        Contours red_contours;
        Contours blue_contours;
    } process_info;
};
}
#endif // COLORDETECT_H
