#include "atlas/solver.hpp"
#include "atlas/checked_principal_range.hpp"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <bit>
#include <cstdlib>
#include "corpus.inc"
#include "history.inc"
#include "checks.inc"
int main(int argc,char**argv){if(argc!=2)return 2;std::string mode=argv[1];if(mode=="corpus")return corpus_study::run();if(mode=="history")return history_study::run();if(mode=="checks")return checks_study::run();return 2;}
