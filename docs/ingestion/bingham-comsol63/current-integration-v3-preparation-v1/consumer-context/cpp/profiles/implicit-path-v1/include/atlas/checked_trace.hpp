#pragma once
#include "atlas/tensor.hpp"

namespace atlas {
// Sticky context failure survives finite arithmetic/predicate masking. A lazy
// unselected branch never executes these helpers. Low-level outputs are scratch.
template<class T>T trace_or_mark(const Sym<T>& a,bool& ok) {
    T result{};
    if(!trace_checked(a,result)) ok=false;
    return result;
}
template<class T>Sym<T> dev_or_mark(const Sym<T>& a,bool& ok) {
    T tr{};
    if(!trace_checked(a,tr)){ok=false;return {};}
    const auto result=a-(tr/T(3))*identity<T>();
    if(!finite_value(result)){ok=false;return {};}
    return result;
}
} // namespace atlas
