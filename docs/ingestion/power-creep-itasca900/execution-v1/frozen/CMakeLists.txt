cmake_minimum_required(VERSION 3.20)
project(PowerCreepQualification LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_executable(atlas_power_creep_solver source/cpp/main.cpp)
target_include_directories(atlas_power_creep_solver PRIVATE source/cpp/include generated)
if(EMSCRIPTEN)
  target_compile_options(atlas_power_creep_solver PRIVATE -fexceptions)
  set_target_properties(atlas_power_creep_solver PROPERTIES OUTPUT_NAME "power-creep" SUFFIX ".js")
  target_link_options(atlas_power_creep_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createPowerCreep"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
