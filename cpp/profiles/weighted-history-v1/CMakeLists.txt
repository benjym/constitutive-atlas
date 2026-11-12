cmake_minimum_required(VERSION 3.20)
project(atlas_weighted_history_v1 LANGUAGES C CXX)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../.." ABSOLUTE)
set(ATLAS_RETAINED_RUNTIME "" CACHE PATH "Exact retained generated candidate runtime")
if(NOT EXISTS "${ATLAS_RETAINED_RUNTIME}/generated/models.hpp")
  message(FATAL_ERROR "Exact retained generated candidate required")
endif()
find_path(ATLAS_BOOST_INCLUDE boost/multiprecision/cpp_bin_float.hpp REQUIRED)
include("${ATLAS_RETAINED_RUNTIME}/cmake/AtlasScalarFunctions.cmake")
add_executable(atlas_weighted_history_check check.cpp)
target_compile_features(atlas_weighted_history_check PRIVATE cxx_std_20)
target_include_directories(atlas_weighted_history_check PRIVATE
  "${ATLAS_ROOT}/cpp/include" "${ATLAS_RETAINED_RUNTIME}/generated" "${ATLAS_BOOST_INCLUDE}")
target_compile_options(atlas_weighted_history_check PRIVATE -fno-fast-math -ffp-contract=off)
if(EMSCRIPTEN)
  target_link_options(atlas_weighted_history_check PRIVATE "-sSTACK_SIZE=1048576")
endif()

find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(ATLAS_WEIGHTED_OVERLAY "${CMAKE_CURRENT_BINARY_DIR}/overlay")
add_custom_command(OUTPUT "${ATLAS_WEIGHTED_OVERLAY}/main.cpp"
  BYPRODUCTS "${ATLAS_WEIGHTED_OVERLAY}/atlas/solver.hpp" "${ATLAS_WEIGHTED_OVERLAY}/atlas/linearize.hpp"
  COMMAND "${Python3_EXECUTABLE}" -B "${CMAKE_CURRENT_SOURCE_DIR}/prepare.py" "${ATLAS_ROOT}" "${ATLAS_WEIGHTED_OVERLAY}"
  DEPENDS prepare.py "${ATLAS_ROOT}/cpp/main.cpp" "${ATLAS_ROOT}/cpp/include/atlas/solver.hpp"
    "${ATLAS_ROOT}/cpp/include/atlas/linearize.hpp" VERBATIM)
add_executable(atlas_weighted_history_solver "${ATLAS_WEIGHTED_OVERLAY}/main.cpp")
target_compile_features(atlas_weighted_history_solver PRIVATE cxx_std_20)
target_include_directories(atlas_weighted_history_solver PRIVATE
  "${ATLAS_WEIGHTED_OVERLAY}" "${CMAKE_CURRENT_SOURCE_DIR}" "${ATLAS_ROOT}/cpp/include"
  "${ATLAS_RETAINED_RUNTIME}/generated" "${ATLAS_BOOST_INCLUDE}")
target_compile_options(atlas_weighted_history_solver PRIVATE -fno-fast-math -ffp-contract=off)
if(EMSCRIPTEN)
  target_compile_options(atlas_weighted_history_solver PRIVATE -fexceptions)
  set_target_properties(atlas_weighted_history_solver PROPERTIES OUTPUT_NAME "weighted-history" SUFFIX ".mjs")
  target_link_options(atlas_weighted_history_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
