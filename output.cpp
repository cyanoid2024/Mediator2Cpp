
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
	int id;
	Port<voteMsg> left(Direction::in);
Port<voteMsg> right(Direction::out);
Port<localMsg> query(Direction::in);
Port<localMsg> notice(Direction::out);

	status leader_status = pending;
voteMsg buffer = { vtype : vote, id : id };
int leaderId = 0;

	Transition transition; TransitionGroup group; TransitionMap map;

	election_module(int id):  id(id)
	{
		
	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return true;
	};
	transition.statements.push_back([]() {
		left.reqRead = (buffer == { vtype : empty_vtype, id : 0 });
	});
	transition.statements.push_back([]() {right.reqWrite = (buffer != null);
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && ((buffer.vtype == vote) && (buffer.id < id)));
	};
	transition.statements.push_back([]() {
		buffer = { vtype : empty_vtype, id : 0 };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && ((buffer.vtype == vote) && (buffer.id == id)));
	};
	transition.statements.push_back([]() {
		buffer.vtype = ack;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && ((buffer.vtype == ack) && (buffer.id < id)));
	};
	transition.statements.push_back([]() {
		buffer = { vtype : vote, id : id };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && ((buffer.vtype == ack) && ((buffer.id >= id) && (buffer.id == id))));
	};
	transition.statements.push_back([]() {
		leader_status = acknowledged;
	});
	transition.statements.push_back([]() {leaderId = buffer.id;
	});
	transition.statements.push_back([]() {buffer = { vtype : empty_vtype, id : 0 };
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && ((buffer.vtype == ack) && ((buffer.id >= id) && (buffer.id != id))));
	};
	transition.statements.push_back([]() {
		leader_status = acknowledged;
	});
	transition.statements.push_back([]() {leaderId = buffer.id;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer == { vtype : empty_vtype, id : 0 }) && left.reqWrite);
	};
	transition.statements.push_back([]() {
		perform left;
	});
	transition.statements.push_back([]() {buffer = left.value;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return ((buffer != { vtype : empty_vtype, id : 0 }) && right.reqRead);
	};
	transition.statements.push_back([]() {
		right.value = buffer;
	});
	transition.statements.push_back([]() {perform right;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return true;
	};
	transition.statements.push_back([]() {
		notice.reqWrite = query.reqWrite;
	});
	transition.statements.push_back([]() {query.reqRead = notice.reqRead;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return (notice.reqRead && notice.reqWrite);
	};
	transition.statements.push_back([]() {
		perform query;
	});
	transition.statements.push_back([]() {notice.value = { leaderStatus : leader_status, localID : id, leaderID : leaderID };
	});
	transition.statements.push_back([]() {perform notice;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);


	}
};



// automaton_def

struct worker{
	int name;
	Port<localMsg> query(Direction::out);
Port<localMsg> notice(Direction::in);

	workerStatus worker_status = waiting;

	Transition transition; TransitionGroup group; TransitionMap map;

	worker(int name):  name(name)
	{
		
	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return (notice.reqWrite && ((notice.value.leaderStatus == acknowledged) && (notice.value.leaderID == notice.value.localID)));
	};
	transition.statements.push_back([]() {
		perform notice;
	});
	transition.statements.push_back([]() {worker_status = leader;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return (notice.reqWrite && ((notice.value.leaderStatus == acknowledged) && (notice.value.leaderID != notice.value.localID)));
	};
	transition.statements.push_back([]() {
		perform notice;
	});
	transition.statements.push_back([]() {worker_status = follower;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return (notice.reqWrite && (notice.value.leaderStatus == pending));
	};
	transition.statements.push_back([]() {
		perform notice;
	});
	transition.statements.push_back([]() {worker_status = waiting;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);



	// transition def

	transition.statements.clear();

	// guard def
	transition.guard = []() -> bool {
		return true;
	};
	transition.statements.push_back([]() {
		query.reqWrite = true;
	});
	transition.statements.push_back([]() {query.value = { leaderStatus : empty_leaderStatus, localID : 0, leaderID : 0 };
	});
	transition.statements.push_back([]() {perform query;
	});
	group.clear();
	group.push_back(transition);
	map.push_back(group);


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

Sync<msgVote> (E1.left, E2.right);
Sync<msgVote> (E2.right, E3.left);
Sync<msgVote> (E3.right, E1.left);
Sync<msgLocal> (C1.query, E1.query);
Sync<msgLocal> (C1.notice, E1.notice);
Sync<msgLocal> (C2.query, E2.query);
Sync<msgLocal> (C2.notice, E2.notice);
Sync<msgLocal> (C3.query, E3.query);
Sync<msgLocal> (C3.notice, E3.notice);
}