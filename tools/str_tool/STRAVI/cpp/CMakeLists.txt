cmake_minimum_required(VERSION 3.10)
project(str_converter)

set(CMAKE_CXX_STANDARD 17)

add_library(str_converter SHARED str_converter.cpp)
