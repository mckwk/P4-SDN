#!/bin/bash

# This script sets up and runs the network topology using Mininet.

# Clean up any existing Mininet instances
sudo mn -c

# Start Mininet with the custom topology
sudo mn --custom ../topology/custom_topo.py --topo mytopo --controller remote --switch ovsk --mac --arp &

# Wait for a few seconds to ensure Mininet is up
sleep 5

# Open a terminal for each host
xterm h1 h2 h3 h4 &

# Run the controller in the background
python3 ../controller/p4runtime_controller.py &

# Wait for the user to terminate the script
wait