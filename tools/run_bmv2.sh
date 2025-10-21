#!/bin/bash

# This script sets up and runs the P4 program on the behavioral model version 2 (bmv2) simulator.

# Exit on error
set -e

# Define the P4 program and the bmv2 target
P4_PROGRAM="src/forwarding.p4"
BMV2_TARGET="bmv2"

# Compile the P4 program
p4c --target $BMV2_TARGET --output-dir build $P4_PROGRAM

# Run the bmv2 simulator
simple_switch --log-file simple_switch.log build/forwarding.json &

# Wait for the simulator to start
sleep 2

# Run the controller
python3 control-plane/controller.py &

# Wait for the user to terminate the script
echo "Press [CTRL+C] to stop the simulation." 
wait