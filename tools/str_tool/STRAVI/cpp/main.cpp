// main.cpp
#include <iostream>
#include <string>
#include "str_converter.h"

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: str_converter [str2avi|avi2str] <file>\n";
        return 1;
    }

    std::string mode = argv[1];
    std::string path = argv[2];

    if (mode == "str2avi") {
        convertStrToAvi(path);
    } else if (mode == "avi2str") {
        convertAviToStr(path);
    } else {
        std::cerr << "Unknown mode: " << mode << "\n";
        return 1;
    }

    return 0;
}
