cmake_minimum_required(VERSION 3.20)
project(AtlasPhysicalTimeV2 LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
include("${ATLAS_ROOT}/cmake/AtlasScalarFunctions.cmake")
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB ATLAS_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py" "${ATLAS_ROOT}/schemas/*.json")
file(GLOB TIME_MODELS CONFIGURE_DEPENDS "${ATLAS_ROOT}/tests/fixtures/time/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -B -m atlas.compiler "${CMAKE_BINARY_DIR}/generated" "${ATLAS_ROOT}/tests/fixtures/time"
  DEPENDS ${TIME_MODELS} ${ATLAS_INPUTS}
  WORKING_DIRECTORY "${ATLAS_ROOT}" VERBATIM)
add_custom_target(atlas_time_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
function(atlas_time_v2_target target source)
  add_executable(${target} "${ATLAS_ROOT}/${source}")
  add_dependencies(${target} atlas_time_models)
  target_include_directories(${target} PRIVATE "${ATLAS_ROOT}/runtimes/physical-time-v2/include" "${ATLAS_ROOT}/cpp/include" "${CMAKE_BINARY_DIR}/generated")
endfunction()
atlas_time_v2_target(atlas_time_solver cpp/main.cpp)
if(EMSCRIPTEN)
  target_compile_options(atlas_time_solver PRIVATE -fexceptions)
  set_target_properties(atlas_time_solver PROPERTIES OUTPUT_NAME time-v2 SUFFIX ".js")
  target_link_options(atlas_time_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
else()
  enable_testing()
  atlas_time_v2_target(atlas_schedule_predictor_tests tests/test_schedule_predictor.cpp)
  atlas_time_v2_target(atlas_time_tests tests/test_time.cpp)
  add_test(NAME atlas_schedule_predictor COMMAND atlas_schedule_predictor_tests)
  add_test(NAME atlas_time COMMAND atlas_time_tests)
endif()
