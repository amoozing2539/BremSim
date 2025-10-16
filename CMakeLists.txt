cmake_minimum_required(VERSION 3.16)
project(Brem_Sim)

find_package(Geant4 REQUIRED COMPONENTS qt)
include(${Geant4_USE_FILE})

include_directories(include)

#finds all .cc files in the src directory
file(GLOB SOURCES "src/*.cc")

add_executable(Brem_Sim Brem_Sim.cc ${SOURCES})
target_link_libraries(Brem_Sim ${Geant4_LIBRARIES})
