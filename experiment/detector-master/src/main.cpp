#include "main.hpp"
#include "args.hpp"
#include "camera.hpp"
#define REALSENSE
#define VISUAL
// #define USE_DEPTH
    float max_value = -700;
    float min_value = 100;

void processImg(dt::BucketDetector &bdt, cv::Mat &img) {
    static clock_t total_start_clock = clock();
    static clock_t frame_end_clock = 0, frame_start_clock = 1;
    frame_end_clock = frame_start_clock;
    frame_start_clock = clock();
    float fps = 1.0f / (frame_start_clock - frame_end_clock) * CLOCKS_PER_SEC;
    printf("fps : %.2f\n", fps);
    bdt.detect(img);
#ifdef VISUAL
    cv::imshow("visualized img", bdt.output_info.visualized_img);
#endif
}

void processKey(dt::BucketDetector &bdt, cam::RsCam &cam) {
    int key = cv::waitKey(1);
    switch (key)
    {
    case 27:
        cam.close();
        break;
    case 'a':
        bdt.visual_config.showRedAndBlueBin = !bdt.visual_config.showRedAndBlueBin;
        break;
    case 'r':
        bdt.visual_config.showRedBin = !bdt.visual_config.showRedBin;
        break;
    case 'b':
        bdt.visual_config.showBlueBin = !bdt.visual_config.showBlueBin;
        break;
    case 'd':
        cam.config.align_to_depth = !cam.config.align_to_depth;
    default:
        break;
    }
}

void processKey(dt::BucketDetector &bdt, cam::Camera &cam) {
    int key = cv::waitKey(1);
    switch (key)
    {
    case 27:
        cam.close();
        break;
    case 'a':
        bdt.visual_config.showRedAndBlueBin = !bdt.visual_config.showRedAndBlueBin;
        break;
    case 'r':
        bdt.visual_config.showRedBin = !bdt.visual_config.showRedBin;
        break;
    case 'b':
        bdt.visual_config.showBlueBin = !bdt.visual_config.showBlueBin;
        break;
    default:
        break;
    }
}

void showCoord(dt::BucketDetector bdt, sp::serialPort msp, proj::Projection pro,cv::Mat depth_img)
{
    cv::Point2i bucketPixelCoord;
    cv::Point3f bucketWorldCoord;
    uint8_t center[2];
    for(int i = 0;i<bdt.output_info.results.size();i++)
    {
        bucketPixelCoord = bdt.output_info.results.at(i).boundingBox.center;
        bucketWorldCoord = pro.pixel2world(bucketPixelCoord,depth_img);
        if(bucketWorldCoord.x > max_value)
            max_value = bucketWorldCoord.x;
        if(bucketWorldCoord.x < min_value)
            min_value = bucketWorldCoord.x;
        //center[0] = (char)bucketWorldCoord.x;
        //center[1] = (char)bucketWorldCoord.y;
        //msp.writeBuffer(center,sizeof(center));
        //msp.readBuffer(center,sizeof(center));
        std::cout<< bucketWorldCoord.x<<'\t'<<bucketWorldCoord.y<<'\t'<<bucketWorldCoord.z << std::endl;
    }
}

int main(int argc, char **argv)
{
    Args args(argc, argv);
    dt::BucketDetector bdt;
    sp::serialPort msp;
    proj::Projection pro;
    rs2_intrinsics depth_intrinics;
    const char *dev = "/dev/ttyUSB0";

#ifdef VISUAL
    bdt.visual_config.visible = true;
#else
    bdt.visual_config.visible = false;
#endif
#ifdef REALSENSE
    cam::RsCam cam(1280, 720, args.fps);
    cam.open();
    depth_intrinics = cam.getIntrinstics();
    pro.setIntrin(depth_intrinics);
#else
    cam::USBCam cam(args.camera);
    cam.open();
#endif
    while (cam.isOpen()) {
        cv::Mat color_img;
        cv::Mat depth_img;
        color_img = cam.read();
        cam.readTo(color_img, depth_img);
        processImg(bdt, color_img);
        processKey(bdt, cam);
        msp.ClosePort();
        //if(msp.OpenPort(dev))
        //{
            showCoord(bdt,msp,pro,depth_img);
        //}
    }
    std::cout<<max_value<<min_value;
    return 0;
}
