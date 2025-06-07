
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


// type_def

enum status { pending, acknowledged, empty_leaderStatus };

// type_def

enum workerStatus { waiting, leader, follower };

// type_def

enum vType { vote, ack, empty_vtype };

// type_def

struct voteMsg {
	vType vtype;  int id; 
	bool operator==(const voteMsg& other) const {
		return vtype == other.vtype && id == other.id;
	};
	bool operator!=(const voteMsg& other) const {
		return !(*this == other);
	};
};

// type_def

struct localMsg {
	status leaderStatus;  int localID;  int leaderID; 
	bool operator==(const localMsg& other) const {
		return leaderStatus == other.leaderStatus && localID == other.localID && leaderID == other.leaderID;
	};
	bool operator!=(const localMsg& other) const {
		return !(*this == other);
	};
};

// automaton_def

struct election_module{
	int elec_id;
	Port<voteMsg> left{ in };
Port<voteMsg> right{ out };
Port<localMsg> query{ in };
Port<localMsg> notice{ out };

	status leader_status = pending;
voteMsg buffer = voteMsg{ vote, elec_id };
int leaderId = 0;

	Transition transition; TransitionGroup group; TransitionMap map;

	election_module(int elec_id):  elec_id(elec_id)
	{
		
	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return true;
	};
	transition.statements.push_back([this,elec_id]() {
		left.reqRead = (buffer == voteMsg{ empty_vtype, 0 });
	});
	transition.statements.push_back([this,elec_id]() {
		right.reqWrite = (buffer != voteMsg{ empty_vtype, 0 });
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && ((buffer.vtype == vote) && (buffer.id < elec_id)));
	};
	transition.statements.push_back([this,elec_id]() {
		buffer = voteMsg{ empty_vtype, 0 };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && ((buffer.vtype == vote) && (buffer.id == elec_id)));
	};
	transition.statements.push_back([this,elec_id]() {
		buffer.vtype = ack;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && ((buffer.vtype == ack) && (buffer.id < elec_id)));
	};
	transition.statements.push_back([this,elec_id]() {
		buffer = voteMsg{ vote, elec_id };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && ((buffer.vtype == ack) && ((buffer.id >= elec_id) && (buffer.id >= elec_id))));
	};
	transition.statements.push_back([this,elec_id]() {
		leader_status = acknowledged;
	});
	transition.statements.push_back([this,elec_id]() {
		leaderId = buffer.id;
	});
	transition.statements.push_back([this,elec_id]() {
		buffer = voteMsg{ empty_vtype, 0 };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && ((buffer.vtype == ack) && ((buffer.id >= elec_id) && (buffer.id != elec_id))));
	};
	transition.statements.push_back([this,elec_id]() {
		leader_status = acknowledged;
	});
	transition.statements.push_back([this,elec_id]() {
		leaderId = buffer.id;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer == voteMsg{ empty_vtype, 0 }) && left.reqWrite);
	};
	transition.statements.push_back([this,elec_id]() {
		perform(left);

	});
	transition.statements.push_back([this,elec_id]() {
		buffer = left.value;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return ((buffer != voteMsg{ empty_vtype, 0 }) && right.reqRead);
	};
	transition.statements.push_back([this,elec_id]() {
		right.value = buffer;
	});
	transition.statements.push_back([this,elec_id]() {
		perform(right);

	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,elec_id]() -> bool {
		return (query.reqRead && notice.reqWrite);
	};
	transition.statements.push_back([this,elec_id]() {
		perform(query);

	});
	transition.statements.push_back([this,elec_id]() {
		notice.value = localMsg{ leader_status, elec_id, leaderId };
	});
	transition.statements.push_back([this,elec_id]() {
		perform(notice);

	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);


	}
void doTransition() {
		processTransitionMap(map);
	}
};



// automaton_def

struct worker{
	int name;
	Port<localMsg> query{ out };
Port<localMsg> notice{ in };

	workerStatus worker_status = waiting;

	Transition transition; TransitionGroup group; TransitionMap map;

	worker(int name):  name(name)
	{
		
	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = [this,name]() -> bool {
		return true;
	};
	transition.statements.push_back([this,name]() {
		query.reqWrite = true;
	});
	transition.statements.push_back([this,name]() {
		query.value = localMsg{ empty_leaderStatus, 0, 0 };
	});
	transition.statements.push_back([this,name]() {
		perform(query);

	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);


	}
void doTransition() {
		processTransitionMap(map);
	}
};



// system_def
int main(){
election_module E1(1);
election_module E2(2);
election_module E3(3);
worker C1(1);
worker C2(2);
worker C3(3);

Sync<voteMsg> (E1.right, E2.left);
Sync<voteMsg> (E2.right, E3.left);
Sync<voteMsg> (E3.right, E1.left);
Sync<localMsg> (C1.query, E1.query);
Sync<localMsg> (C1.notice, E1.notice);
Sync<localMsg> (C2.query, E2.query);
Sync<localMsg> (C2.notice, E2.notice);
Sync<localMsg> (C3.query, E3.query);
Sync<localMsg> (C3.notice, E3.notice);
}
