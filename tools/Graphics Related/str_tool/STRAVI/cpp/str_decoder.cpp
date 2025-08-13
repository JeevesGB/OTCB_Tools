#include "str_decoder.h"
#include <iostream>
#include <cstring>

bool is_mdec_video_sector(const std::vector<uint8_t>& sector) {
    if (sector.size() != 2352) return false;
    if (sector[0] != 0x00 || sector[11] != 0xFF) return false;
    if (sector[15] != 2) return false; // Mode 2
    return (sector[18] & 0x04) != 0; // Submode: video bit
}

std::vector<uint8_t> extract_mdec_payload(const std::vector<uint8_t>& sector) {
    return std::vector<uint8_t>(sector.begin() + 24, sector.end());
}

std::vector<uint8_t> decode_mdec_to_rgb(const std::vector<uint8_t>& mdec_data) {
    // Dummy implementation: simulate RGB output
    int width = 320, height = 240;
    std::vector<uint8_t> rgb(width * height * 3);
    for (int i = 0; i < rgb.size(); ++i) {
        rgb[i] = static_cast<uint8_t>((i + mdec_data[0]) % 256);
    }
    return rgb;
}

void write_avi_header(std::ostream& out, int width, int height, int fps, int total_frames) {
    // Minimal placeholder for demonstration
    char header[64] = {0};
    std::memcpy(header, "FAKEAVI", 7); // placeholder signature
    out.write(header, sizeof(header));
}

void write_avi_frame(std::ostream& out, const std::vector<uint8_t>& rgb) {
    out.write(reinterpret_cast<const char*>(rgb.data()), rgb.size());
}

void finalize_avi(std::ostream& out) {
    // Nothing for now
}
