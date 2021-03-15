#include "args.hpp"
#include <iostream>

namespace {
    using doc_t = const char* const;
    doc_t helpDoc = "Display help.";
    doc_t cameraDoc = "camera id";
    doc_t paramDocI = "<int>";
    doc_t paramDocB = "<flag>";
    doc_t paramDocF = "<float>";
    doc_t paramDocUint8 = "<uint8>";
}

Args::Args(int argc, char** argv)
    : camera(0),
      fps(30),
      realsense(false),
      use_depth(false),
      mParser(),
      mHelp(false),
      mDefaults(false),
      mList(false) {

    // add commands
    mParser.add("\nHelp:");
    mParser.add("--help", helpDoc, mHelp);
    mParser.add("--camera", cameraDoc, camera);
    mParser.add("--fps", "set fps", fps);
    mParser.add("--rs", "whether to use realsense", realsense);
    mParser.add("--depth", "whether to use depth", use_depth);
    // parse command-line
    mParser.parse(argc, argv);

    // if requested, display help and exit
    if (mHelp) {
        mParser.printHelp(std::cerr);
        std::exit(-1);
    }

    // if requested, display defaults and exit
    if (mDefaults) {
        mDefaults = false;
        mParser.printValues(std::cerr, '\n');
        std::exit(-1);
    }

    // validate parameters, throw if there is trouble
    validate();
}

void Args::validate() const {
}
