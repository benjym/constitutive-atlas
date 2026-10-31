"""Python-only audit of candidate limb transcription and generated bit fixtures.

No compilation or execution of C++ is performed. This cannot certify C++ syntax,
compiler floating arithmetic, undefined behavior, native/Wasm parity or throughput.
"""
from fractions import Fraction
from pathlib import Path
import json
import math
import random
import re
import struct

HERE=Path(__file__).resolve().parent
MASK=(1<<64)-1

def bitvalue(x):return struct.unpack('>d',struct.pack('>Q',x))[0]
def bits(x):return struct.unpack('>Q',struct.pack('>d',x))[0]
def word_add(a,i,x):
    while x and i<len(a):
        old=a[i];a[i]=(old+x)&MASK;x=int(a[i]<old);i+=1
    assert x==0

def limb_sum(bs):
    positive=[0]*34;negative=[0]*34
    for b in bs:
        e=(b>>52)&2047;assert e!=2047
        sig=(b&((1<<52)-1))|((1<<52)if e else 0)
        shift=e-1 if e else 0;i,offset=divmod(shift,64)
        a=negative if b>>63 else positive
        word_add(a,i,(sig<<offset)&MASK)
        if offset:word_add(a,i+1,sig>>(64-offset))
    order=next((1 if a>b else -1 for a,b in zip(positive[::-1],negative[::-1])if a!=b),0)
    if order==0:return 0
    a,b=(positive,negative)if order>0 else(negative,positive)
    magnitude=[];borrow=0
    for x,y in zip(a,b):
        z=(x-y)&MASK;first=x<y;v=(z-borrow)&MASK;second=z<borrow
        magnitude.append(v);borrow=int(first or second)
    assert borrow==0
    top=next(i*64+magnitude[i].bit_length()-1 for i in range(33,-1,-1)if magnitude[i])
    sign=(1<<63)if order<0 else 0
    if top<52:return sign|magnitude[0]
    shift=top-52;word,offset=divmod(shift,64);q=magnitude[word]>>offset
    if offset and word+1<34:q|=(magnitude[word+1]<<(64-offset))&MASK
    q&=(1<<53)-1
    if shift:
        guard=(magnitude[(shift-1)//64]>>((shift-1)%64))&1
        full,rest=divmod(shift-1,64)
        sticky=any(magnitude[:full])or(rest!=0 and magnitude[full]&((1<<rest)-1)!=0)
        if guard and(sticky or q&1):q+=1
    if q==1<<53:q>>=1;shift+=1
    exponent=shift+1
    if exponent>=2047:return None
    return sign|(exponent<<52)|(q&((1<<52)-1))

def exact(bs):
    total=sum((Fraction.from_float(bitvalue(b))for b in bs),Fraction())
    try:out=float(total)
    except OverflowError:return None
    return bits(out)if out else 0

def rows():
    text=(HERE/'trace_fixtures.hpp').read_text()
    matches=re.findall(r'\{"([^"\n]+)",\{\{([^}]+)\}\},(true|false),0x([0-9a-f]+)ULL\}',text)
    out=[]
    for name,values,ok,value in matches:
        bs=[int(x.removeprefix('0x').removesuffix('ULL'),16)for x in values.split(',')]
        out.append((name,bs,int(value,16)if ok=='true'else None))
    return out

def check():
    fixtures=rows();assert len(fixtures)==97
    for name,bs,expected in fixtures:assert limb_sum(bs)==exact(bs)==expected,name
    rng=random.Random(20261031)
    for _ in range(12000):
        bs=[rng.getrandbits(64)for _ in range(3)]
        bs=[b^(1<<52)if(b>>52)&2047==2047 else b for b in bs]
        assert limb_sum(bs)==exact(bs)
    # Every normal exponent and carry/borrow alignment boundary, both signs.
    for e in range(1,2047):
        for f in [0,(1<<52)-1]:
            b=(e<<52)|f
            for small in [1,1<<51,1<<52]:
                bs=[b,small,b|(1<<63)];assert limb_sum(bs)==exact(bs)
    h=(HERE/'trace_accuracy_candidate.hpp').read_text()
    assert 'std::array<std::uint64_t,34>'in h and 'std::fegetround()==FE_TONEAREST'in h
    assert 'new 'not in h and 'std::vector'not in h and 'atlas/model'not in h
    return {'version':'trace-candidate-source-check-v1','fixture_rows':97,'random_fraction_trials':12000,'exponent_alignment_trials':2046*2*3,'all_checks_passed':True,'cpp_compiled':False,'cpp_executed':False}

if __name__=='__main__':print(json.dumps(check(),indent=2))
