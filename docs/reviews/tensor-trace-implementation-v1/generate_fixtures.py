"""Transport frozen independent Fraction corpus into C++ bit constants."""
from pathlib import Path
import hashlib
import json
import struct

HERE=Path(__file__).resolve().parent

def generate(corpus):
    rows=json.loads(corpus.read_text())['records']
    def bits(x):return struct.unpack('>Q',struct.pack('>d',float.fromhex(x)))[0]
    out=['#pragma once','#include <array>','#include <cstdint>',
         'struct TraceFixture{const char* id;std::array<std::uint64_t,3> input;bool ok;std::uint64_t expected;};',
         'inline constexpr std::array<TraceFixture,97> trace_fixtures={{']
    assert len(rows)==97
    for r in rows:
        inp=','.join('0x%016xULL'%bits(x)for x in r['inputs_hex'])
        out.append('{'+json.dumps(r['id'])+',{{'+inp+'}},'+str(r['ok']).lower()+',0x'+(r['expected_bits']if r['ok']else'0000000000000000')+'ULL},')
    out+=['}};']
    return '\n'.join(out)+'\n'

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True);p.add_argument('--check',action='store_true');a=p.parse_args()
    text=generate(a.corpus);target=HERE/'trace_fixtures.hpp'
    if a.check:assert target.read_text()==text
    else:
        assert not target.exists(),'fresh generated fixture path required';target.write_text(text)
