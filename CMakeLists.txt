cmake_minimum_required(VERSION 3.20)
project(ConstitutiveAtlas VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
file(GLOB MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/generated"
  DEPENDS ${MODEL_FILES} atlas/dsl.py atlas/model.py atlas/compiler.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp" "${CMAKE_BINARY_DIR}/generated/models.json")
add_executable(atlas_solver cpp/main.cpp)
add_dependencies(atlas_solver atlas_models)
target_include_directories(atlas_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
target_compile_options(atlas_solver PRIVATE -Wall -Wextra -Wno-unused-variable)
if(EMSCRIPTEN)
  target_compile_options(atlas_solver PRIVATE -fexceptions)
  set_target_properties(atlas_solver PROPERTIES OUTPUT_NAME "atlas" SUFFIX ".js")
  target_link_options(atlas_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
else()
  enable_testing()
  add_executable(atlas_numerical_tests tests/test_solver.cpp)
  add_dependencies(atlas_numerical_tests atlas_models)
  target_include_directories(atlas_numerical_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/generated")
  add_test(NAME atlas_numerical COMMAND atlas_numerical_tests)
  add_executable(atlas_tensor_square_tests tests/test_tensor_square.cpp)
  target_include_directories(atlas_tensor_square_tests PRIVATE cpp/include)
  add_test(NAME atlas_tensor_square COMMAND atlas_tensor_square_tests)
  add_test(NAME atlas_python COMMAND "${Python3_EXECUTABLE}" -m unittest discover -s tests -v)
  set_tests_properties(atlas_python PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}" ENVIRONMENT "ATLAS_SOLVER=$<TARGET_FILE:atlas_solver>;ATLAS_TIME_SOLVER=$<TARGET_FILE:atlas_time_solver>")
endif()

# Synthetic integration fixtures use the same compiler and engine, but a separate
# generated catalogue. They are never packaged as public atlas models.
file(GLOB TIME_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/tests/fixtures/time/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/time-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/time-generated" "${CMAKE_SOURCE_DIR}/tests/fixtures/time"
  DEPENDS ${TIME_MODEL_FILES} atlas/dsl.py atlas/model.py atlas/compiler.py atlas/structure.py schemas/model.schema.json schemas/model-v0.2.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_time_models DEPENDS "${CMAKE_BINARY_DIR}/time-generated/models.hpp")
add_executable(atlas_time_solver cpp/main.cpp)
add_dependencies(atlas_time_solver atlas_time_models)
target_include_directories(atlas_time_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_time_solver PRIVATE -fexceptions)
  set_target_properties(atlas_time_solver PROPERTIES OUTPUT_NAME "time-fixtures" SUFFIX ".js")
  get_target_property(ATLAS_WASM_OPTIONS atlas_solver LINK_OPTIONS)
  target_link_options(atlas_time_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  add_executable(atlas_time_tests tests/test_time.cpp)
  add_dependencies(atlas_time_tests atlas_time_models)
  target_include_directories(atlas_time_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
  add_test(NAME atlas_time COMMAND atlas_time_tests)
  add_executable(atlas_capacity_tests tests/test_capacity.cpp)
  add_dependencies(atlas_capacity_tests atlas_time_models)
  target_include_directories(atlas_capacity_tests PRIVATE cpp/include "${CMAKE_BINARY_DIR}/time-generated")
  add_test(NAME atlas_capacity COMMAND atlas_capacity_tests)
endif()

# Source-pinned research drafts stay separate from both admitted browser models
# and synthetic verification fixtures. They use exactly the same compiler/engine.
file(GLOB RESEARCH_MODEL_FILES CONFIGURE_DEPENDS "${CMAKE_SOURCE_DIR}/models/research/*.json")
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/research-generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/research-generated" "${CMAKE_SOURCE_DIR}/models/research"
  DEPENDS ${RESEARCH_MODEL_FILES} atlas/dsl.py atlas/model.py atlas/compiler.py atlas/structure.py schemas/model-v0.2.schema.json schemas/model.schema.json
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
add_custom_target(atlas_research_models DEPENDS "${CMAKE_BINARY_DIR}/research-generated/models.hpp")
add_executable(atlas_research_solver cpp/main.cpp)
add_dependencies(atlas_research_solver atlas_research_models)
target_include_directories(atlas_research_solver PRIVATE cpp/include "${CMAKE_BINARY_DIR}/research-generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_research_solver PRIVATE -fexceptions)
  set_target_properties(atlas_research_solver PROPERTIES OUTPUT_NAME "research" SUFFIX ".js")
  target_link_options(atlas_research_solver PRIVATE ${ATLAS_WASM_OPTIONS})
else()
  set_property(TEST atlas_python APPEND PROPERTY ENVIRONMENT "ATLAS_RESEARCH_SOLVER=$<TARGET_FILE:atlas_research_solver>")
endif()
