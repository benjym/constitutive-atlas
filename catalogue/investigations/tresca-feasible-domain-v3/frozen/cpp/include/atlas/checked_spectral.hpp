#pragma once
#include "atlas/numerics/symmetric_spectral.hpp"
namespace atlas {
// Value-only results are allowed only through statically validated predicates.
// Their zero Jet storage is transport, not a claimed mathematical derivative.
template<class T>T spectral_scalar_or_mark(const Sym<T>&a,spectral_candidate::Operation operation,bool&ok){
    T result{};spectral_candidate::Diagnostic diagnostic;
    if(!spectral_candidate::scalar_checked(a,operation,result,diagnostic))ok=false;
    return result;
}
template<class T>Sym<T> spectral_projector_or_mark(const Sym<T>&a,spectral_candidate::Operation operation,bool&ok){
    Sym<T> result{};spectral_candidate::Diagnostic diagnostic;
    if(!spectral_candidate::projector_checked(a,operation,result,diagnostic))ok=false;
    return result;
}
} // namespace atlas
