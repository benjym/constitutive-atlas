#pragma once
#include "trace/tensor.hpp"
#include "trace/numerics/determinant.hpp"

namespace atlas_trace {
// Mark every executed determinant failure, including finite predicate masking.
// The surrounding evaluation context owns the sticky flag and scratch outputs.
// Unselected lazy branches do not call this helper.
template<class T> T determinant_or_mark(const Sym<T>& a, bool& ok) {
    T result{};
    if (!determinant_accuracy::checked(a, result)) ok = false;
    return result;
}
} // namespace atlas_trace
