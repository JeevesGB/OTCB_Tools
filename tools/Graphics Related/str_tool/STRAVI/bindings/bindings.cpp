#include "str_decoder.h"
#include <cstring>

extern "C" {

    STRDecoder* create_decoder(const char* filepath) {
        return new STRDecoder(filepath);
    }

    bool decode_str(STRDecoder* decoder) {
        return decoder->decode();
    }

    void destroy_decoder(STRDecoder* decoder) {
        delete decoder;
    }

}
