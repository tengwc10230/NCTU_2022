#include <bits/stdc++.h>
#include <unistd.h>

using std::cout;
using std::endl;
using std::string;

inline uint64_t micros()
{
    uint64_t us = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch())
            .count();
    return us; 
}

int main(int argc, char *argv[])
{
    // std::ios_base::sync_with_stdio(0), std::cin.tie(0);
    if (argc != 3)
    {
        cout << "[executable file name] [input file name] [output file name]\n";
        return 0;
    }
    std::ifstream fin(argv[1], std::ios::in);
    std::ofstream fout(argv[2], std::ios::out);
    if (!fin.is_open())
        cout << "Failed to open in file\n";
    else if (!fout.is_open())
        cout << "Failed to open out file\n";
    else {
        uint64_t start = micros();
        string str;
        std::getline(fin, str);
        double balance_factor = stod(str);
        
        std::unordered_map<string, std::vector<string>> cell_array;
        std::unordered_map<string, std::vector<string>> net_array;
        // cell_array.reserve(1048576); // 2^24
        // net_array.reserve(1048576); // 2^24

        string NET_NAME; 
        char *token;
        while (std::getline(fin, str)) {
            token = strtok(const_cast<char*>(str.c_str()), " ");
            while (token != NULL) {
                if (token == "NET")
                {
                    token = strtok(NULL, " ");
                    NET_NAME = token;
                }
                else if (token != ";"){
                    // cout << token << " ";
                    cell_array[token].push_back(NET_NAME);
                    net_array[NET_NAME].push_back(token);
                }
                token = strtok(NULL, " ");
            }
            // else if (str != "") {
            //     cell_array[str].push_back(NET_NAME);
            //     net_array[NET_NAME].push_back(str);
            // }
        }
        uint64_t read_time = micros() - start;
        cout << read_time << '\n';
    }
    
}