CC = g++
CFLAGS = -g -O2 -std=c++11
P4C = p4c-bm
P4_SRC = p4/path_switch.p4
P4_INFO = path_switch.p4info
BM_JSON = path_switch.json

all: build run

build:
	$(P4C) --json $(BM_JSON) --p4info-file $(P4_INFO) $(P4_SRC)

run:
	./tools/run_topology.sh & \
	python3 controller/p4runtime_controller.py

clean:
	rm -f $(BM_JSON) $(P4_INFO)