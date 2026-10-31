from pathlib import Path
import hashlib,json
r=Path('/Users/bmar5496/code/constitutive-atlas');p=Path(__file__).resolve().parent
old=(r/'atlas/dsl.py').read_text()
replacement='''def trace(a):
    """Nearest-even exact sum of binary64 diagonals; validate full tensor."""
    if not isinstance(a, Sym) or len(a.v) != 6:
        raise ValidationError("trace requires a six-component symmetric tensor")
    values = []
    for value in a.v:
        if type(value) not in (int, float):
            raise ValidationError("trace requires finite real components")
        try:
            value = float(value)
        except (OverflowError, ValueError) as exc:
            raise ValidationError("trace requires finite real components") from exc
        if not math.isfinite(value):
            raise ValidationError("trace requires finite real components")
        values.append(value)
    try:
        result = float(sum((Fraction.from_float(v) for v in values[:3]), Fraction()))
    except OverflowError as exc:
        raise ValidationError("trace final sum overflows binary64") from exc
    return 0. if result == 0. else result


def dev(a):
    result = a - I * (trace(a) / 3)
    if not all(math.isfinite(v) for v in result.v):
        raise ValidationError("deviator result is nonfinite")
    return result
'''
start=old.index('def trace(a):');end=old.index('\n\ndef dot(a, b):',start)
new=old[:start]+replacement.rstrip()+old[end:]
new=new.replace("        if name=='log1p': return", "        if name in ('trace', 'dev'): return f\"atlas::{name}_or_mark({cpp(node.args[0])}, atlas_eval_ok)\"\n        if name=='log1p': return")
(p/'dsl.py').write_text(new)
oldheader=(r/'cpp/include/atlas/tensor.hpp').read_text();anchor='template<class T>Sym<T> dev(const Sym<T>&a){return a-(trace(a)/T(3))*identity<T>();}'
newheader=oldheader.replace(anchor,anchor+'''
template<class T>T trace_or_mark(const Sym<T>&a,bool& ok){
    T result{};
    if(!trace_checked(a,result)) ok=false;
    return result;
}
template<class T>Sym<T> dev_or_mark(const Sym<T>&a,bool& ok){
    T tr{};
    if(!trace_checked(a,tr)){ok=false;return {};}
    const auto result=a-(tr/T(3))*identity<T>();
    if(!finite_value(result)){ok=false;return {};}
    return result;
}''')
assert new!=old and newheader!=oldheader
(p/'tensor.hpp').write_text(newheader)
(p/'input-receipt.json').write_text(json.dumps({'original_sources':{str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [r/'atlas/dsl.py',r/'cpp/include/atlas/tensor.hpp']},'candidate_sources':{f:hashlib.sha256((p/f).read_bytes()).hexdigest() for f in ['dsl.py','tensor.hpp']},'compiled_observations':False},indent=2)+'\n')
print('Prepared bounded checked-trace/checked-dev candidate; production unchanged')
