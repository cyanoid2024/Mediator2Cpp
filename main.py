# -*- coding: utf-8 -*-

from Parser import parse
from Parser import tree_to_dict
from Generator import Generator
# from z3 import *
import json
from pprint import pprint

def parse_file(model_name):
    with open(model_name, 'r', encoding='utf-8') as test_file:
        model_code = test_file.read()

    parsed_model = parse(model_code)
    with open(model_name+"parsed.json", "w") as f:
        json.dump(parsed_model, f, indent=2)
    return parsed_model



header = """
// head

#include <cstdlib>
#include <ctime>
// #include <enumeration>
#include <functional>
#include <iostream>
#include<iomanip>
#include <memory>
//#include <mpi.h>
#include <optional>
#include <random>
#include <string>
#include <thread>
#include <unordered_map>
#include <variant>
#include <vector>



// head-port

int in = 0;
int out = 1;
#include <iostream>
#include <optional>

template <typename T>
struct Port {
    int p_direction;
    bool reqRead = false;
    bool reqWrite = false;
    // std::optional<T> value;
    T value;

    // neighborhood of ports
    std::vector<std::shared_ptr<Port<T>>> nbhd;
    void addNbhd(std::shared_ptr<Port<T>> neighbor) {
        nbhd.push_back(neighbor);
    }
    

    Port(int& dir, T& init_val) 
        : p_direction(dir), value(init_val) {}

    Port(int& dir) 
        : p_direction(dir) {}
};

template <typename T1>
void Sync(Port<T1> port1, Port<T1> port2) {
    port1.addNbhd(port2);
    port2.addNbhd(port1);
}

template <typename T3>
void perform(Port<T3> port) {
    // Perform some operation with the port
    if (port.p_direction == in && port.reqRead) {
        for (const auto& portnb : port.nbhd) {
            if (portnb->p_direction == out) {
                
                port.value = portnb->value; // Assuming we want to read the value
            }
        }
    }
    if (port.p_direction == out && port.reqWrite) {
        for (const auto& portnb : port.nbhd) {
            if (portnb->p_direction == in) {
                
                portnb->value = port.value;
            }
        }
        
    }
}

template <typename T2>
void perform(Port<T2> port){

}

// head-transition
using Statement = std::function<void()>;
using Guard = std::function<bool()>;

struct Transition {
    Guard guard;
    std::vector<Statement> statements;
};

using TransitionGroup = std::vector<Transition>;

using TransitionMap = std::vector<TransitionGroup>;

// PROBLEM: ONLY GROUP-TRANSITION IS SUPPORTED

void executeTransition(const Transition& transition) {
    for (const auto& statement : transition.statements) {
        statement();
    }
}

void processTransitionMap(const TransitionMap& transitionMap) {
    srand(static_cast<unsigned int>(time(nullptr)));
    size_t groupIndex = 0;

    while (true) {
        const TransitionGroup& group = transitionMap[groupIndex];
        // choose a random transition from the current group
        size_t transitionIndex = rand() % group.size(); 
        const Transition& transition = group[transitionIndex];

        // guard returns true, execute the transition
        if (transition.guard()) {
            executeTransition(transition);
            break; 
        }

        // move to the next group
        groupIndex = (groupIndex + 1) % transitionMap.size();
    }
}

"""

def main():
    parsed_model = parse_file('models/leader_3.med')
    

    generator = Generator(parsed_model)
    cpp_code = header
    cpp_code += generator.generate()
    # pprint(cpp_code)

    with open('output.cpp', 'w') as f:
        f.write(cpp_code)

if __name__ == "__main__":
    main()
