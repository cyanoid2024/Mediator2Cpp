# -*- coding: utf-8 -*-

from Parser import parse
from Parser import tree_to_dict
from Parser import pre_parse
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

// #include <enumeration>
#include <functional>
#include <iostream>
#include<iomanip>
#include <memory>
#include <mpi.h>
#include <optional>
#include <random>
#include <string>
#include <thread>
#include <unordered_map>
#include <variant>
#include <vector>



// head-port

enum Direction { in, out };
#include <iostream>
#include <optional>

template <typename T>
struct Port {
    Direction p_direction;
    bool reqRead = false;
    bool reqWrite = false;
    std::optional<T> value;

    Port(Direction dir, T init_val) 
        : p_direction(dir), value(init_val) {}

    Port(Direction dir) 
        : p_direction(dir) {}
};

void Sync(Port<T> port1, Port<T> port2) {
    // Synchronize two ports
}


// head-transition
using Statement = std::function<void()>;
using Guard = std::function<bool()>;

struct Transition {
    Guard guard;
    std::vector<Statement> statements;
};
// Transition transition; // not here

using TransitionGroup = std::vector<Transition>;
// TransitionGroup group; // not here

using TransitionMap = std::vector<TransitionGroup>;
// TransitionMap map; // not here
// PROBLEM: ONLY GROUP-TRANSITION IS SUPPORTED
// lan de gai le hao fan
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