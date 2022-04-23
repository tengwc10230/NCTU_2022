#include <bits/stdc++.h>
#include <unistd.h>
#include <chrono>

using std::cout;
using std::endl;
using std::string;

// inline uint64_t micros()
// {
//     uint64_t us = std::chrono::duration_cast<std::chrono::microseconds>(
//             std::chrono::high_resolution_clock::now().time_since_epoch())
//             .count();
//     return us; 
// }

int main(int argc, char* argv[])
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
        // uint64_t start = micros();
        string str;
        fin >> str;
        double balance_factor = stod(str);
        
        std::unordered_map<string, std::vector<string>> cell_array;
        std::unordered_map<string, std::vector<string>> net_array;
        cell_array.reserve(1048576); // 2^24
        net_array.reserve(1048576); // 2^24

        string NET_NAME; 
        while (fin >> str) {
            if (str == "NET")
                fin >> NET_NAME;
            else if (str != ";") {
                cell_array[str].push_back(NET_NAME);
                net_array[NET_NAME].push_back(str);
            }
        }
        // uint64_t read_time = micros() - start;

        int C = cell_array.size();
        int N = net_array.size();
        int S = balance_factor * cell_array.size() / 2;
        int cut_size = 0;
      
        std::unordered_set<string> G1;
        std::unordered_set<string> G2;
        G1.reserve(C);
        G2.reserve(C);
        
        // init partition
        for (auto &c : cell_array) {
            if (G1.size() < C/2) 
                G1.insert(c.first);
            else
                G2.insert(c.first);
        }

        // Initialize all cell gains in O(P) time
        std::unordered_map<string, int> cell_gain;
        cell_gain.reserve(C);
        for (auto &c : cell_array)  cell_gain[c.first] = 0;
          
        // assign each cell gain
        for (auto &n_c : net_array) {
            int G1_num = 0, G2_num = 0;
            string G1_last_cell = "", G2_last_cell = "";
            for (auto &c : n_c.second) {
                if (G1.find(c) != G1.end()) {
                    G1_num ++;
                    G1_last_cell = c;
                }
                else {
                    G2_num ++;
                    G2_last_cell = c;
                }
                if (G1_num >= 2 && G2_num >= 2)
                    break;
            }
            // in this net "from block" F is 1 for one cell
            if (G1_num == 1)    cell_gain[G1_last_cell] ++;
            if (G2_num == 1)    cell_gain[G2_last_cell] ++;
            // in this net "to block" T = 0
            if (G1_num == 0 || G2_num == 0)
                for (auto &c : n_c.second)
                    cell_gain[c] --;
        }

        // put cell into gan_list
        std::unordered_map<int, std::unordered_set<string>> G1_gan_list; 
        std::unordered_map<int, std::unordered_set<string>> G2_gan_list; 
        int max_gain_G1 = INT_MIN;
        int max_gain_G2 = INT_MIN;
        G1_gan_list.reserve(C);
        G2_gan_list.reserve(C);

        for (auto &c_g : cell_gain)
        {
            if (G1.find(c_g.first) != G1.end())
            {
                G1_gan_list[c_g.second].insert(c_g.first);
                if (c_g.second > max_gain_G1)
                    max_gain_G1 = c_g.second;
            }
            else
            {
                G2_gan_list[c_g.second].insert(c_g.first);
                if (c_g.second > max_gain_G2)
                    max_gain_G2 = c_g.second;
            }
        }
        std::unordered_set<string> locked_cell;
        
        while (1) {
             // select and move cell
            string moved_cell = "";
            
            if ((max_gain_G1 >= max_gain_G2 || G2.size() == C/2 + S) && G1.size() > C/2 - S) {
                moved_cell = *(G1_gan_list[max_gain_G1].begin());
                G1.erase(moved_cell);
                G2.insert(moved_cell);
                G1_gan_list[max_gain_G1].erase(moved_cell);

                if (max_gain_G1 < 0)
                    break;
            }
            else {
                moved_cell = *(G2_gan_list[max_gain_G2].begin());
                G2.erase(moved_cell);
                G1.insert(moved_cell);
                G2_gan_list[max_gain_G2].erase(moved_cell);

                if (max_gain_G2 < 0)
                    break;
            }
            // cout << moved_cell << '\n';
            locked_cell.insert(moved_cell);
            // recompute gains of ¡§touched¡¨ cellsx
            for (auto &n : cell_array[moved_cell])
            {
                int G1_num = 0, G2_num = 0;
                string G1_last_cell, G2_last_cell;
                for (auto &c : net_array[n])
                {
                    if (G1.find(c) != G1.end()) {
                        G1_num ++;
                        G1_last_cell = c;
                    }
                    else {
                        G2_num ++;
                        G2_last_cell = c;
                    }
                    if (G1_num >= 2 && G2_num >= 2)
                        break;
                }
                if (G1_num == 1)
                {
                    if (locked_cell.find(G1_last_cell) == locked_cell.end()) {
                        G1_gan_list[cell_gain[G1_last_cell]].erase(G1_last_cell);
                        cell_gain[G1_last_cell] ++;
                        G1_gan_list[cell_gain[G1_last_cell]].insert(G1_last_cell);
                    }
                }    
                if (G2_num == 1)
                {
                    if (locked_cell.find(G2_last_cell) == locked_cell.end()) {
                        G2_gan_list[cell_gain[G2_last_cell]].erase(G2_last_cell);
                        cell_gain[G2_last_cell] ++;
                        G2_gan_list[cell_gain[G2_last_cell]].insert(G2_last_cell);
                    }
                }    
                if (G1_num == 0 || G2_num == 0) {
                    for (auto &c : net_array[n]) {
                        if (locked_cell.find(c) == locked_cell.end())
                        {
                            if (G2_num == 0) {
                                G1_gan_list[cell_gain[c]].erase(c);
                                cell_gain[c] --;
                                G1_gan_list[cell_gain[c]].insert(c);
                            }
                            if (G1_num == 0) {
                                G2_gan_list[cell_gain[c]].erase(c);
                                cell_gain[c] --;
                                G2_gan_list[cell_gain[c]].insert(c);
                            }
                        }
                    }
                }
            }
            
            // max gain search
            max_gain_G1 = INT_MIN;
            max_gain_G2 = INT_MIN;
            for (auto &g_l : G1_gan_list) {
                if (g_l.first > max_gain_G1 && !g_l.second.empty())
                    max_gain_G1 = g_l.first;
            }
            for (auto &g_l : G2_gan_list) {
                if (g_l.first > max_gain_G2 && !g_l.second.empty())
                    max_gain_G2 = g_l.first;
            }
        }
        
        for (auto &n : net_array) {
            bool in_G1 = false, in_G2 = false;
            for (auto &c : n.second) {
                if (G1.find(c) != G1.end())
                    in_G1 = true;
                else if (G2.find(c) != G2.end())
                    in_G2 = true;
                
                if (in_G1 && in_G2) {
                    cut_size ++;
                    break;
                }
            }
        }

        // uint64_t run_time = micros() - start - read_time;

        fout << "Cutsize = " << cut_size << "\n";
        fout << "G1 " << G1.size() << "\n";
        for (auto &c : G1)
            fout << c << " ";
        fout << ";\n";
        fout << "G2 " << G2.size() << "\n";
        for (auto &c : G2)
            fout << c << " ";
        fout << ";\n";
        
        fin.close();
        fout.close();   
        
        // uint64_t write_time = micros() - start - read_time - run_time;

        // cout << "read_time: " << read_time << '\n';
        // cout << "run_time: " << run_time << '\n';
        // cout << "write_time " << write_time << '\n';
    }
}