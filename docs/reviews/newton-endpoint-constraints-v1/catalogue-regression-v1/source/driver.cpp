#define main original_main
#include "test_solver.cpp"
#undef main
int main(){setenv("ATLAS_NATIVE_FIXTURES","explicit-gis20-occ-v3",1);return original_main();}
