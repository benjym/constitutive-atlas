cmake_minimum_required(VERSION 3.20)
project(ConstitutiveAtlas VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/generated"
  DEPENDS ${MODEL_FILES} atlas/dsl.py atlas/model.py atlas/compiler.py atlas/structure.py schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_solver cpp/main.cpp)
add_dependencies(atlas_solver atlas_models)
target_include_directories(atlas_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  set_target_properties(atlas_solver PROPERTIES OUTPUT_NAME "atlas" SUFFIX ".js")
  target_link_options(atlas_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-sDISABLE_EXCEPTION_CATCHING=0"
    "-sFILESYSTEM=0" "--no-entry")
else()
  enable_testing()
  add_executable(atlas_numerical_tests tests/test_solver.cpp)
  add_dependencies(atlas_numerical_tests atlas_models)
  target_include_directories(atlas_numerical_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
  add_test(NAME atlas_numerical COMMAND atlas_numerical_tests)
  add_test(NAME atlas_python COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s tests -v)
  set_tests_properties(atlas_python PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" ENVIRONMENT "ATLAS_SOLVER=$<TARGET_FILE:atlas_solver>")
endif()
