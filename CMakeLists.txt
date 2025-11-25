cmake_minimum_required(VERSION 3.16)
project(BremSim)

find_package(Geant4 REQUIRED COMPONENTS qt)

include(${Geant4_USE_FILE})
include_directories(${PROJECT_SOURCE_DIR}/include)

#finds all .cc files in the src directory
file(GLOB SOURCES "${PROJECT_SOURCE_DIR}/source/*.cc")
file(GLOB HEADERS "${PROJECT_SOURCE_DIR}/include/*.hh")

add_executable(BremSim BremSim.cc ${SOURCES} ${HEADERS})
target_link_libraries(BremSim ${Geant4_LIBRARIES})
