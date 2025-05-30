#include "str_converter.h"
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: str_converter str2avi|avi2str <file_path>\n";
        return 1;
    }

    std::string mode = argv[1];
    std::string path = argv[2];

    if (mode == "str2avi") {
        return convert_str_to_avi(path);
    } else {
        std::cerr << "Unsupported mode: " << mode << "\n";
        return 1;
    }
}
