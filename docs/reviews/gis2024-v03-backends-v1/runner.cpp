// Test-only persistent transport over the unmodified generic production C ABI.
#define main atlas_original_cli_main
#include "cpp/main.cpp"
#undef main
int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        if (line == "D") { std::cout << atlas_describe() << std::endl; continue; }
        std::vector<std::string> fields; std::istringstream input(line); std::string item;
        while (std::getline(input, item, '\t')) fields.push_back(item);
        if (fields.size() != 6 || fields[0] != "I") return 3;
        std::cout << atlas_integrate_with_settings(fields[1].c_str(), fields[2].c_str(),
            fields[3].c_str(), fields[4].c_str(), fields[5].c_str()) << std::endl;
    }
    return 0;
}
