#pragma once
#include "trace/tensor.hpp"
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace atlas_trace::history {
constexpr std::uint64_t max_counter=9007199254740991ULL;
inline double hcheck(double value) {
    if (!std::isfinite(value)) throw std::runtime_error("nonfinite history expression");
    return value;
}
inline bool hcheck(bool value) { return value; }
inline Sym<double> hcheck(Sym<double> value) {
    for (double x : value.v) hcheck(x);
    return value;
}
struct Result {
    bool ok=false;
    std::vector<double> values;
    std::uint64_t generation=0, epoch=0;
    std::vector<int> events;
    int attempted=0, executed=0, failed=-1;
    std::string message;
};
using Advance=Result (*)(const std::vector<double>&, const std::vector<double>&, std::uint64_t, std::uint64_t);
struct Program {
    const char* id;
    const char* sha256;
    std::size_t state_size, input_size;
    Advance advance;
};
} // namespace atlas_trace::history
