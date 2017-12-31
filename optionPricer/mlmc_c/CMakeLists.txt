cmake_minimum_required(VERSION 2.6)

project (MLMC)

add_executable (MLMC payoff.cpp option.cpp main.cpp model.cpp utils.cpp)

add_definitions(-DsrcPath="${CMAKE_CURRENT_SOURCE_DIR}")
