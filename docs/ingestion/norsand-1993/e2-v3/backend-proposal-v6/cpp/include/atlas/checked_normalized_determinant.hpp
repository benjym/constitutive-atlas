#pragma once
#include "atlas/tensor.hpp"
#include "atlas/numerics/normalized_determinant.hpp"
namespace atlas {
// Every executed failure stays sticky, including predicates/eager masking.
// Unselected lazy branches do not call the helper.
template<class T>T normalized_determinant_or_mark(const Sym<T>&a,bool&ok){
    T result{};
    if(!normalized_determinant_accuracy::checked(a,result))ok=false;
    return result;
}
} // namespace atlas
