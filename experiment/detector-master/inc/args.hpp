#ifndef FMO_DESKTOP_ARGS_HPP
#define FMO_DESKTOP_ARGS_HPP

#include "parser.hpp"

/// Processes and verifies command-line arguments.
struct Args {
    /// Read arguments from the command line. Throws exceptions if there are any errors.
    Args(int argc, char** argv);

    int camera;                      ///< camera ID to use as input
    float fps;                       ///< set fps
    bool realsense;
    bool use_depth;
    void printParameters(std::ostream& out, char sep) const { mParser.printValues(out, sep); }

private:
    void validate() const;

    Parser mParser;
    bool mHelp;     ///< display help
    bool mDefaults; ///< display defaults for all parameters
    bool mList;     ///< display algorithm list
};

#endif // FMO_DESKTOP_ARGS_HPP
