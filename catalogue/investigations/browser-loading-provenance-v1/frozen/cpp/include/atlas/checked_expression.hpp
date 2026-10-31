#pragma once
#include "atlas/tensor.hpp"

namespace atlas {
// Check every executed AST boundary, including all Jet columns. Return by value
// to preserve type and lifetime. Never clear a failure recorded by a sibling.
template<class T> inline T expression_or_mark(const T& value, bool& ok) {
    if (!finite_value(value)) ok = false;
    return value;
}
} // namespace atlas
