#pragma once
#include <vector>
#include <cstdint>
#include <ostream>

bool is_mdec_video_sector(const std::vector<uint8_t>& sector);
std::vector<uint8_t> extract_mdec_payload(const std::vector<uint8_t>& sector);
std::vector<uint8_t> decode_mdec_to_rgb(const std::vector<uint8_t>& mdec_data);  // Fake RGB decoder for now
void write_avi_header(std::ostream& out, int width, int height, int fps, int total_frames);
void write_avi_frame(std::ostream& out, const std::vector<uint8_t>& rgb);
void finalize_avi(std::ostream& out);
