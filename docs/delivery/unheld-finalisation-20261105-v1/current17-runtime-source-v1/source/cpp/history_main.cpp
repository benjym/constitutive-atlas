#include "history_programs.hpp"
#include <charconv>
#include <cstdlib>
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define HISTORY_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define HISTORY_EXPORT
#endif

namespace {
std::string quote(const std::string& s) {
    std::ostringstream out; out << '"';
    for (unsigned char c : s) {
        if (c=='"' || c=='\\') out << '\\' << c;
        else if (c<32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << int(c) << std::dec;
        else out << c;
    }
    out << '"'; return out.str();
}
std::uint64_t counter(const char* text) {
    if (!text || !*text) throw std::invalid_argument("missing history counter");
    std::string s(text);
    if (s.size()>16 || s.find_first_not_of("0123456789")!=std::string::npos || (s.size()>1 && s[0]=='0'))
        throw std::invalid_argument("history counter must be canonical unsigned decimal");
    std::uint64_t value=0;
    auto parsed=std::from_chars(s.data(),s.data()+s.size(),value);
    if (parsed.ec!=std::errc{} || value>atlas::history::max_counter)
        throw std::invalid_argument("history counter outside exact integer range");
    return value;
}
std::vector<double> numbers(const char* text, std::size_t expected) {
    if (!text) throw std::invalid_argument("missing history numeric wire");
    std::string s(text);
    if (s.size()>262144) throw std::invalid_argument("history numeric wire too long");
    std::vector<double> result;
    if (s.empty() && expected==0) return result;
    std::size_t start=0;
    while (start<=s.size()) {
        if (result.size()>=expected) throw std::invalid_argument("too many history components");
        auto end=s.find(',',start); if (end==std::string::npos) end=s.size();
        auto token=s.substr(start,end-start);
        if (token.empty() || token.find_first_not_of("0123456789.eE+-")!=std::string::npos)
            throw std::invalid_argument("invalid history numeric token");
        // strtod is available in native libc and Emscripten; require exact consumption.
        char* tail=nullptr; const double value=std::strtod(token.c_str(),&tail);
        if (tail!=token.c_str()+token.size() || !std::isfinite(value))
            throw std::invalid_argument("nonfinite or malformed history component");
        result.push_back(value);
        if (end==s.size()) break;
        start=end+1;
    }
    if (result.size()!=expected) throw std::invalid_argument("history component count mismatch");
    return result;
}
std::string execute(const char* id, const char* hash, const char* state, const char* inputs,
                    const char* generation, const char* epoch) {
    try {
        if (!id || !hash) throw std::invalid_argument("missing history identity");
        const atlas::history::Program* selected=nullptr;
        for (const auto& p : atlas::history::programs()) if (std::string(id)==p.id) selected=&p;
        if (!selected || std::string(hash)!=selected->sha256) throw std::invalid_argument("history program identity/hash mismatch");
        const auto g=counter(generation), e=counter(epoch);
        const auto parent=numbers(state,selected->state_size), arguments=numbers(inputs,selected->input_size);
        const auto r=selected->advance(parent,arguments,g,e);
        std::ostringstream out; out << std::setprecision(17);
        out << "{\"valid\":true,\"ok\":" << (r.ok?"true":"false")
            << ",\"program_sha256\":" << quote(selected->sha256)
            << ",\"generation\":" << r.generation << ",\"preparation_epoch\":" << r.epoch << ",\"values\":[";
        for (std::size_t i=0;i<r.values.size();i++) { if (i) out << ','; out << r.values[i]; }
        out << "],\"events\":[";
        for (std::size_t i=0;i<r.events.size();i++) { if (i) out << ','; out << r.events[i]; }
        out << "],\"diagnostics\":{\"attempted_phases\":" << r.attempted
            << ",\"executed_phases\":" << r.executed << ",\"failed_phase\":" << r.failed
            << "},\"message\":" << quote(r.message) << '}';
        return out.str();
    } catch (const std::exception& error) {
        return "{\"valid\":false,\"ok\":false,\"message\":"+quote(error.what())+"}";
    }
}
}
extern "C" {
HISTORY_EXPORT const char* atlas_history_describe() { return atlas::history::description(); }
HISTORY_EXPORT const char* atlas_history_advance(const char* id, const char* hash, const char* state,
                                               const char* inputs, const char* generation, const char* epoch) {
    static thread_local std::string output;
    output=execute(id,hash,state,inputs,generation,epoch); return output.c_str();
}
}
#ifndef __EMSCRIPTEN__
int main(int argc, char** argv) {
    if (argc==2 && std::string(argv[1])=="--describe") { std::cout << atlas_history_describe() << '\n'; return 0; }
    const std::vector<std::string> keys={"--program","--hash","--state","--inputs","--generation","--epoch"};
    std::map<std::string,const char*> args;
    for (int i=1;i+1<argc;i+=2) {
        if (std::find(keys.begin(),keys.end(),argv[i])==keys.end() || !args.emplace(argv[i],argv[i+1]).second) {
            std::cerr << "unknown or duplicate history argument\n"; return 2;
        }
    }
    if (argc!=13 || args.size()!=6) { std::cerr << "six named history wire arguments required\n"; return 2; }
    const auto output=execute(args[keys[0]],args[keys[1]],args[keys[2]],args[keys[3]],args[keys[4]],args[keys[5]]);
    std::cout << output << '\n'; return output.find("\"valid\":true")==std::string::npos?2:0;
}
#endif
