cmake_minimum_required(VERSION 3.20)
project(atlas_controlled_path LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(ATLAS_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
set(ATLAS_PATH_MODELS "${ATLAS_ROOT}/models/research/norsand/norsand-jefferies-1993-active-axial.json" CACHE STRING "Explicit controlled-path model files")
file(GLOB ATLAS_PYTHON CONFIGURE_DEPENDS "${ATLAS_ROOT}/atlas/*.py")
set(ATLAS_GENERATED "${CMAKE_CURRENT_BINARY_DIR}/generated")
add_custom_command(
 OUTPUT "${ATLAS_GENERATED}/path_api.cpp" "${ATLAS_GENERATED}/path_models.hpp" "${ATLAS_GENERATED}/path_catalogue.json"
 COMMAND "${Python3_EXECUTABLE}" "${ATLAS_ROOT}/tools/generate_controlled_path.py" --output "${ATLAS_GENERATED}" ${ATLAS_PATH_MODELS}
 DEPENDS ${ATLAS_PATH_MODELS} ${ATLAS_PYTHON} "${ATLAS_ROOT}/schemas/model-v0.3.schema.json" "${ATLAS_ROOT}/tools/generate_controlled_path.py"
 VERBATIM)
if(EMSCRIPTEN)
 add_executable(atlas_path_capability "${ATLAS_GENERATED}/path_api.cpp")
 target_link_options(atlas_path_capability PRIVATE --no-entry -sMODULARIZE=1 -sEXPORT_ES6=1 -sENVIRONMENT=node,web,worker -sALLOW_MEMORY_GROWTH=1 "-sEXPORTED_FUNCTIONS=['_path_size','_path_evaluate','_path_advance','_malloc','_free']" "-sEXPORTED_RUNTIME_METHODS=['ccall','cwrap','HEAPF64']" -fexceptions)
 target_compile_options(atlas_path_capability PRIVATE -fexceptions)
 set_target_properties(atlas_path_capability PROPERTIES SUFFIX ".mjs")
else()
 add_library(atlas_path_capability SHARED "${ATLAS_GENERATED}/path_api.cpp")
endif()
target_include_directories(atlas_path_capability PRIVATE "${ATLAS_ROOT}/cpp/include" "${ATLAS_GENERATED}")
target_compile_options(atlas_path_capability PRIVATE -Wall -Wextra -Wpedantic -fno-fast-math -ffp-contract=off)
