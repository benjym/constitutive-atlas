from pathlib import Path
p=Path(__file__).parent/'proposed/cpp/include/atlas/solver.hpp';s=p.read_text();s=s.replace('Point committed;committed.state=initial;','Point committed;committed.control=controls?controls->front():0.;committed.state=initial;',1);p.write_text(s)
p=Path(__file__).parent/'proposed/cpp/main.cpp';s=p.read_text().replace('#include <cstdlib>','#include <cstdlib>\n#include <cstdint>\n#include <cstring>\n#include <limits>')
pos=s.index('int model_index(')
new='''// Exact finite binary64 wire, independent of decimal conversion and libm.
// Canonical lowercase uint64 hexadecimal, 16 digits per cumulative control.
atlas::State parse_control_bits(const char*csv){
    static_assert(sizeof(double)==sizeof(std::uint64_t)&&std::numeric_limits<double>::is_iec559,"binary64 controls require IEEE double");
    if(!csv)throw std::runtime_error("missing explicit control bits");
    const std::string wire(csv);atlas::State controls;
    if(wire.size()<33||wire.size()>85016)throw std::runtime_error("explicit controls require 2..5001 binary64 hex values");
    size_t start=0;
    while(start<wire.size()){
        const size_t end=wire.find(',',start),count=(end==std::string::npos?wire.size():end)-start;
        if(count!=16||controls.size()>=5001)throw std::runtime_error("control bits require exactly 16 lowercase hex digits");
        std::uint64_t bits=0;
        for(size_t j=start;j<start+16;++j){const char c=wire[j];
            if(!((c>='0'&&c<='9')||(c>='a'&&c<='f')))throw std::runtime_error("control bits require exactly 16 lowercase hex digits");
            bits=(bits<<4)|std::uint64_t(c<='9'?c-'0':c-'a'+10);
        }
        double value;std::memcpy(&value,&bits,sizeof value);
        if(!std::isfinite(value))throw std::runtime_error("explicit controls must be finite");
        controls.push_back(value);
        if(end==std::string::npos)break;
        start=end+1;if(start==wire.size())throw std::runtime_error("trailing control comma");
    }
    return controls;
}
void control_bits(std::ostream&o,const atlas::State&controls){
    o<<'[';for(size_t i=0;i<controls.size();++i){if(i)o<<',';std::uint64_t bits;std::memcpy(&bits,&controls[i],sizeof bits);
        std::ostringstream hex;hex<<std::hex<<std::setfill('0')<<std::setw(16)<<bits;o<<quote(hex.str());}o<<']';
}
'''
s=s[:pos]+new+s[pos:]
s=s.replace('auto controls=parse_csv(controls_csv);return run_response','auto controls=parse_control_bits(controls_csv);return run_response',1)
s=s.replace('const char*controls_csv,const char*settings){','const char*controls_csv,const char*settings){',1)
old='array(o,*controls);o<<"},\\\"steps\\\":"'
new='array(o,*controls);o<<",\\\"encoding\\\":\\\"ieee754-binary64-hex\\\",\\\"controls_bits\\\":";control_bits(o,*controls);o<<"},\\\"steps\\\":"'
assert old in s;s=s.replace(old,new,1);p.write_text(s)
