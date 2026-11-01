cmake_minimum_required(VERSION 3.20)
project(AtlasMaxwell LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB ATLAS_INPUTS CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py" "${ATLAS_ROOT}/schemas/*.json")
file(GLOB MAXWELL_MODELS CONFIGURE_DEPENDS "${ATLAS_ROOT}/models/research/maxwell/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -B -m atlas.compiler "${CMAKE_BINARY_DIR}/generated" "${ATLAS_ROOT}/models/research/maxwell"
  DEPENDS ${MAXWELL_MODELS} ${ATLAS_INPUTS}
  WORKING_DIRECTORY "${ATLAS_ROOT}" VERBATIM)
add_custom_target(atlas_maxwell_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_maxwell_solver EXCLUDE_FROM_ALL "${ATLAS_ROOT}/cpp/main.cpp")
add_dependencies(atlas_maxwell_solver atlas_maxwell_models)
target_include_directories(atlas_maxwell_solver PRIVATE "${ATLAS_ROOT}/cpp/include" "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_maxwell_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_maxwell_solver PRIVATE -fexceptions)
  set_target_properties(atlas_maxwell_solver PROPERTIES OUTPUT_NAME maxwell SUFFIX ".js")
  target_link_options(atlas_maxwell_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions" "-sFILESYSTEM=0" "--no-entry")
endif()
