#pragma once
#include <algorithm>
#include <stdexcept>
namespace atlas {
// Internal evaluation scope: all input derivative columns from count-1 onward
// must be bitwise identical. The last calculated column represents that tail.
inline thread_local int derivative_columns=38;
inline int derivative_work_columns(){return derivative_columns;}
class DerivativeTailScope {
 int previous;
public:
 explicit DerivativeTailScope(int count):previous(derivative_columns){if(count<1||count>38)throw std::invalid_argument("invalid derivative tail scope");derivative_columns=count;}
 ~DerivativeTailScope(){derivative_columns=previous;}
 DerivativeTailScope(const DerivativeTailScope&)=delete;
 DerivativeTailScope& operator=(const DerivativeTailScope&)=delete;
};
template<class J>inline void fill_derivative_tail(J&x){const int count=derivative_work_columns();if(count<int(x.d.size()))std::fill(x.d.begin()+count,x.d.end(),x.d[count-1]);}
}
